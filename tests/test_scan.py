"""State restoration checks; opt in to real Tao with BMAD_SKILL_RUNTIME_TESTS=1."""
from __future__ import annotations

import csv
import importlib.util
import io
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/bmad-ecosystem/scripts/scan_quadrupole.py"
spec = importlib.util.spec_from_file_location("scan_quadrupole", SCRIPT)
scan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scan)


class FakeTao:
    """Small session double: inject faults at the mutation/observation boundary."""

    def __init__(self):
        self.k1 = 1.2345678901234567
        self.original = self.k1
        self.commands = []
        self.calc_on = True
        self.fail_observation = False
        self.nan_observation = False
        self.fail_restore = False
        self.key = "Quadrupole"

    def tao_global(self):
        return {"lattice_calc_on": self.calc_on}

    def lat_list(self, selector, who, **kwargs):
        if who == "ele.ix_ele":
            return {"QF": [2], "END": [6], "D_HALF": [1, 5]}[selector]
        if who == "ele.k1" and selector == "2":
            return [self.k1]
        raise AssertionError((selector, who))

    def ele_head(self, locator, **kwargs):
        return {"key": self.key}

    def cmd(self, command):
        self.commands.append(command)
        value = float(command.split("=")[1])
        if self.fail_restore and value == self.original:
            raise RuntimeError("injected restoration failure")
        self.k1 = value
        return []

    def ele_twiss(self, locator, **kwargs):
        if self.fail_observation:
            raise RuntimeError("injected optics failure")
        return {"beta_a": float("nan") if self.nan_observation else 10 + self.k1,
                "alpha_a": 0.0, "beta_b": 10 - self.k1, "alpha_b": 0.0}


class ScanStateTests(unittest.TestCase):
    def test_success_preserves_the_exact_original_strength(self):
        tao = FakeTao()
        rows = scan.scan_quadrupole(tao, [0.8, 1.0, 1.2])
        self.assertEqual([row["k1_m^-2"] for row in rows], [0.8, 1.0, 1.2])
        self.assertEqual(tao.k1.hex(), tao.original.hex())
        self.assertIn("1@0>>2", tao.commands[-1])

    def test_observation_failure_restores_strength(self):
        tao = FakeTao()
        tao.fail_observation = True
        with self.assertRaisesRegex(RuntimeError, "injected optics failure"):
            scan.scan_quadrupole(tao, [0.8])
        self.assertEqual(tao.k1, tao.original)

    def test_invalid_optics_restores_strength(self):
        tao = FakeTao()
        tao.nan_observation = True
        with self.assertRaisesRegex(ValueError, "beta_a must be finite"):
            scan.scan_quadrupole(tao, [0.8])
        self.assertEqual(tao.k1, tao.original)

    def test_invalid_strengths_are_rejected_before_mutation(self):
        tao = FakeTao()
        with self.assertRaisesRegex(ValueError, "K1 must be finite"):
            scan.scan_quadrupole(tao, [0.8, float("nan")])
        self.assertEqual(tao.commands, [])

    def test_stale_optics_are_not_reported_as_new_results(self):
        tao = FakeTao()
        tao.calc_on = False
        with self.assertRaisesRegex(ValueError, "lattice_calc_on"):
            scan.scan_quadrupole(tao, [0.8])
        self.assertEqual(tao.commands, [])

    def test_ambiguous_observation_does_not_change_the_lattice(self):
        tao = FakeTao()
        with self.assertRaisesRegex(ValueError, "found 2"):
            scan.scan_quadrupole(tao, [0.8], observe="D_HALF")
        self.assertEqual(tao.commands, [])

    def test_wrong_element_type_does_not_change_the_lattice(self):
        tao = FakeTao()
        tao.key = "Drift"
        with self.assertRaisesRegex(ValueError, "not a quadrupole"):
            scan.scan_quadrupole(tao, [0.8])
        self.assertEqual(tao.commands, [])

    def test_restoration_failure_is_explicit(self):
        tao = FakeTao()
        tao.fail_restore = True
        with self.assertRaisesRegex(RuntimeError, "Failed to restore original K1"):
            scan.scan_quadrupole(tao, [0.8])


def matmul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(2)) for j in range(2)] for i in range(2)]


def expected_twiss(plane):
    """Independent thick-lens transport with input beta=10m, alpha=0."""
    def drift(length):
        return [[1.0, length], [0.0, 1.0]]

    def quadrupole(k, length):
        q = math.sqrt(abs(k))
        if k > 0:
            c, s = math.cos(q * length), math.sin(q * length)
            return [[c, s / q], [-q * s, c]]
        c, s = math.cosh(q * length), math.sinh(q * length)
        return [[c, s / q], [q * s, c]]

    m = [[1.0, 0.0], [0.0, 1.0]]
    for step in [drift(.5), quadrupole(plane, .2), drift(1), quadrupole(-plane, .2), drift(.5)]:
        m = matmul(step, m)
    beta = 10 * m[0][0] ** 2 + .1 * m[0][1] ** 2
    alpha = -10 * m[0][0] * m[1][0] - .1 * m[0][1] * m[1][1]
    return beta, alpha


@unittest.skipUnless(os.environ.get("BMAD_SKILL_RUNTIME_TESTS") == "1", "requires an installed PyTao/Tao runtime")
class RealTaoTests(unittest.TestCase):
    def setUp(self):
        from pytao import SubprocessTao
        self.directory = tempfile.TemporaryDirectory(prefix="bmad-skill-test-")
        self.addCleanup(self.directory.cleanup)
        shutil.copytree(scan.ASSETS, self.directory.name, dirs_exist_ok=True)
        self.tao = SubprocessTao(init_file="tao.init", noplot=True, cwd=self.directory.name)
        self.addCleanup(self.tao.close_subprocess)

    def test_fodo_matches_independent_linear_transport(self):
        twiss = self.tao.ele_twiss("1@0>>END", which="model")
        for name, plane in (("a", 1), ("b", -1)):
            beta, alpha = expected_twiss(plane)
            self.assertAlmostEqual(twiss[f"beta_{name}"], beta, places=10)
            self.assertAlmostEqual(twiss[f"alpha_{name}"], alpha, places=10)

    def test_scan_changes_optics_and_restores_full_precision(self):
        original = 1.2345678901234567
        self.tao.cmd(f"set element 1@0>>2 k1 = {original:.17g}")
        rows = scan.scan_quadrupole(self.tao, [0.8, 1.0, 1.2])
        self.assertEqual(len({row["beta_a_m"] for row in rows}), 3)
        restored = float(self.tao.lat_list("2", "ele.k1", ix_uni="1", ix_branch="0")[0])
        self.assertEqual(restored.hex(), original.hex())

    def test_cli_produces_csv_from_the_copied_example(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "--k1", "0.9", "1.1"],
                                check=True, text=True, capture_output=True, timeout=30)
        rows = list(csv.DictReader(io.StringIO(result.stdout)))
        self.assertEqual([float(row["k1_m^-2"]) for row in rows], [0.9, 1.1])
        self.assertEqual(list(scan.ASSETS.glob("*.digested*")), [])


if __name__ == "__main__":
    unittest.main()
