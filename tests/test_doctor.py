"""Doctor must give an honest machine-readable diagnosis without a runtime."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "skills/bmad-ecosystem/scripts/doctor.py"
spec = importlib.util.spec_from_file_location("doctor", SCRIPT)
doctor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(doctor)


class DoctorTests(unittest.TestCase):
    def test_missing_python_package_is_diagnostic_data(self):
        with patch.object(doctor.importlib, "import_module", side_effect=ModuleNotFoundError("No module named 'pytao'")):
            result = doctor.diagnose()
        self.assertFalse(result["pytao"]["importable"])
        self.assertFalse(result["libtao"]["loadable"])
        self.assertIn("ModuleNotFoundError", result["pytao"]["error"])

    def test_required_runtime_returns_failure_and_valid_json(self):
        report = {"pytao": {"importable": True}, "libtao": {"loadable": False, "error": "not found"}}
        stream = io.StringIO()
        with patch.object(doctor, "diagnose", return_value=report), contextlib.redirect_stdout(stream):
            code = doctor.main(["--require-runtime"])
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(stream.getvalue()), report)


if __name__ == "__main__":
    unittest.main()
