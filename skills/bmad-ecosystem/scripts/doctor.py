#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Report the active Python/PyTao/Tao runtime without changing its configuration.

Import PyTao and test loading libtao, but do not initialize a lattice or run Tao
commands. A successful library load is not an end-to-end physics test; run the
bundled scan to check that. --require-runtime makes missing PyTao/libtao an error.
"""

from __future__ import annotations

import argparse
import importlib
import importlib.metadata
import inspect
import json
import os
from pathlib import Path
import platform
import shutil
import sys
from typing import Any


def diagnose() -> dict[str, Any]:
    report: dict[str, Any] = {
        "python": {"executable": sys.executable, "version": platform.python_version()},
        "tao_executable": shutil.which("tao"),
        "pytao": {"importable": False},
        "libtao": {"loadable": False},
        "environment": {
            name: os.environ.get(name)
            for name in ("CONDA_PREFIX", "ACC_ROOT_DIR", "TAO_DIR", "PYTAO_LIB_PATH")
        },
        "note": "Library loading does not verify lattice initialization or optics; run scan_quadrupole.py for that.",
    }
    try:
        package = importlib.import_module("pytao")
        report["pytao"].update(
            importable=True, version=importlib.metadata.version("pytao"),
            module=package.__file__, tao_signature=str(inspect.signature(package.Tao)),
        )
    except Exception as exc:
        report["pytao"]["error"] = f"{type(exc).__name__}: {exc}"
    if report["pytao"]["importable"]:
        try:
            core = importlib.import_module("pytao.core")
            _library, path = core.init_libtao()
            report["libtao"].update(loadable=True, path=path)
        except Exception as exc:
            report["libtao"]["error"] = f"{type(exc).__name__}: {exc}"
    # When available, preserve the package version/build alongside Python's.
    for metadata in (Path(sys.prefix) / "conda-meta").glob("bmad-*.json"):
        try:
            data = json.loads(metadata.read_text(encoding="utf-8"))
            report["bmad_conda_package"] = {key: data[key] for key in ("version", "build")}
        except (OSError, ValueError, KeyError):
            continue
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-runtime", action="store_true", help="Exit 1 if PyTao or libtao is unavailable")
    args = parser.parse_args(argv)
    report = diagnose()
    print(json.dumps(report, indent=2))
    ready = report["pytao"]["importable"] and report["libtao"]["loadable"]
    return int(args.require_runtime and not ready)


if __name__ == "__main__":
    raise SystemExit(main())
