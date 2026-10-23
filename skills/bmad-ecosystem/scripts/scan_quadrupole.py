#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Scan one quadrupole's model K1 and restore it, using a separate Tao process.

Requires PyTao and a compatible libtao. Run --help without either dependency.
The default open FODO line specifies its initial Twiss parameters; it does not
compute a periodic ring solution. Values are sampled at the observation
element's downstream end. All strengths are absolute K1 values in m^-2.
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
import re
import shutil
import sys
import tempfile
from typing import Any, Iterable


FIELDS = ("k1_m^-2", "beta_a_m", "alpha_a", "beta_b_m", "alpha_b")
ASSETS = Path(__file__).resolve().parents[1] / "assets" / "fodo"


def finite(value: Any, label: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label} must be finite; received {value!r}")
    return result


def resolve_element(tao: Any, selector: str, universe: int, branch: int) -> int:
    """Resolve a name or index to exactly one tracking element."""
    if not re.fullmatch(r"[A-Za-z0-9_.:+-]+", selector):
        raise ValueError("Use an element name or index; pass its universe/branch separately")
    matches = tao.lat_list(
        selector, "ele.ix_ele", ix_uni=str(universe), ix_branch=str(branch),
        which="model", flags="-array_out -track_only",
    )
    if len(matches) != 1:
        raise ValueError(f"Expected one element for {selector!r}; found {len(matches)}")
    return int(matches[0])


def scan_quadrupole(
    tao: Any,
    strengths: Iterable[float],
    *,
    element: str = "QF",
    observe: str = "END",
    universe: int = 1,
    branch: int = 0,
) -> list[dict[str, float]]:
    """Return completed scan rows; restore the original K1 even on an exception.

    Use PyTao's numeric array API to snapshot K1. The text returned by
    ele_gen_attribs can round the last bits, which is unsuitable for exact
    restoration. Keep lattice calculation enabled throughout; reject a session
    with calculation disabled before changing it.
    """
    values = [finite(value, "K1") for value in strengths]
    if not values:
        raise ValueError("Provide at least one K1 value")
    if universe < 1 or branch < 0:
        raise ValueError("Universe must be positive and branch must be nonnegative")
    if not tao.tao_global()["lattice_calc_on"]:
        raise ValueError("Enable lattice_calc_on before scanning; otherwise optics may be stale")

    target = resolve_element(tao, element, universe, branch)
    observed = resolve_element(tao, observe, universe, branch)
    locator = f"{universe}@{branch}>>{target}"
    observation = f"{universe}@{branch}>>{observed}"
    if tao.ele_head(locator, which="model")["key"].lower() != "quadrupole":
        raise ValueError(f"{locator} is not a quadrupole")

    def read_k1() -> float:
        result = tao.lat_list(
            str(target), "ele.k1", ix_uni=str(universe), ix_branch=str(branch),
            which="model", flags="-array_out -track_only",
        )
        if len(result) != 1:
            raise RuntimeError(f"K1 query for {locator} did not return one value")
        return finite(result[0], f"K1 at {locator}")

    def set_k1(value: float) -> None:
        tao.cmd(f"set element {locator} k1 = {value:.17g}")
        if read_k1() != value:
            raise RuntimeError(f"Tao did not retain the requested K1 at {locator}")

    original = read_k1()
    rows: list[dict[str, float]] = []
    try:
        for value in values:
            set_k1(value)
            twiss = tao.ele_twiss(observation, which="model")
            beta_a = finite(twiss["beta_a"], "beta_a")
            beta_b = finite(twiss["beta_b"], "beta_b")
            if beta_a <= 0 or beta_b <= 0:
                raise ValueError("Tao returned nonpositive beta; inspect the optics calculation")
            rows.append({
                "k1_m^-2": value,
                "beta_a_m": beta_a,
                "alpha_a": finite(twiss["alpha_a"], "alpha_a"),
                "beta_b_m": beta_b,
                "alpha_b": finite(twiss["alpha_b"], "alpha_b"),
            })
    finally:
        try:
            set_k1(original)
        except Exception as exc:
            raise RuntimeError(f"Failed to restore original K1={original:.17g} at {locator}") from exc
    return rows


def run(init: Path, args: argparse.Namespace) -> list[dict[str, float]]:
    from pytao import SubprocessTao

    # Match relative lattice/include paths to the chosen init file's directory.
    # A custom init can execute its own startup commands and write output files.
    with SubprocessTao(init_file=init.name, noplot=True, cwd=init.parent) as tao:
        return scan_quadrupole(
            tao, args.k1, element=args.element, observe=args.observe,
            universe=args.universe, branch=args.branch,
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--init", type=Path, help="Use a trusted tao.init; relative files resolve beside it")
    parser.add_argument("--element", default="QF", help="One quadrupole name or tracking index (default: QF)")
    parser.add_argument("--observe", default="END", help="One observation element name or index (default: END)")
    parser.add_argument("--universe", type=int, default=1)
    parser.add_argument("--branch", type=int, default=0)
    parser.add_argument("--k1", type=float, nargs="+", default=[0.8, 1.0, 1.2], help="Absolute strengths in m^-2")
    parser.add_argument("--output", type=Path, help="Create a new CSV file; default: standard output")
    args = parser.parse_args(argv)
    try:
        if args.init:
            init = args.init.expanduser().resolve(strict=True)
            rows = run(init, args)
        else:
            with tempfile.TemporaryDirectory(prefix="bmad-fodo-") as temporary:
                folder = Path(temporary) / "fodo"
                shutil.copytree(ASSETS, folder)
                rows = run(folder / "tao.init", args)
        # Emit results only after a complete scan and successful restoration.
        if args.output:
            with args.output.expanduser().open("x", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=FIELDS)
                writer.writeheader()
                writer.writerows(rows)
        else:
            writer = csv.DictWriter(sys.stdout, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
    except Exception as exc:
        print(f"Scan failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
