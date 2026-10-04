"""Portable behavior checks; no proprietary SDK or AE runtime required by CI."""
import importlib.util
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("calibration_oracle", ROOT / "experiments/startup_calibration/oracle.py")
oracle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oracle)


class StartupCalibrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder = tempfile.TemporaryDirectory(prefix="aehl-calibration-tests-")
        cls.binary = Path(cls.folder.name) / "core"
        compiler = shutil.which("clang++") or shutil.which("g++")
        if not compiler:
            cls.folder.cleanup()
            raise RuntimeError("C++ compiler unavailable")
        try:
            subprocess.run([compiler, "-std=c++17", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
                str(ROOT / "tests/startup_calibration_core.cpp"), "-o", str(cls.binary)],
                check=True, stdin=subprocess.DEVNULL, capture_output=True, timeout=60)
        except BaseException:
            cls.folder.cleanup()
            raise

    @classmethod
    def tearDownClass(cls):
        cls.folder.cleanup()

    def test_one_shot_opaque_cursor_reentry_partial_failure_and_project_guards(self):
        result = subprocess.run([str(self.binary)], check=True, capture_output=True, timeout=15)
        self.assertEqual(result.stdout, b"CALIBRATION_CORE_CASES=36 PASS; Adobe_calls=0; render=NOT_RUN\n")

    def test_bounded_own_name_projection_cursor_refusals_and_monotonic_schedule(self):
        result = subprocess.run([str(self.binary), "names"], check=True, capture_output=True, timeout=15)
        self.assertEqual(result.stdout, b"NAME_PROJECTION_CASES=15 PASS; Adobe_calls=0; apply=NOT_RUN\n")

    def test_native_kernel_agrees_with_independent_oracle_and_preserves_padding(self):
        data = subprocess.run([str(self.binary), "pixels"], check=True, capture_output=True, timeout=15).stdout
        result = oracle.compare(data, 19, 11, 0x345678, stride=83)
        self.assertEqual(result["pixel_status"], "PASS")
        for row in range(11):
            self.assertEqual(data[row * 83 + 76:(row + 1) * 83], b"\xA5" * 7)

    def test_oracle_rejects_wrong_seed_order_corruption_and_alpha(self):
        frame = oracle.expected(5, 3, 0x345678)
        for seed, order in [(0x345679, "ARGB8"), (0x345678, "RGBA8")]:
            self.assertEqual(oracle.compare(frame, 5, 3, seed, order)["pixel_status"], "FAIL")
        for index in (0, 5, len(frame) - 1):
            changed = bytearray(frame); changed[index] ^= 1
            self.assertEqual(oracle.compare(changed, 5, 3, 0x345678)["differing_channels"], 1)

    def test_oracle_rejects_truncation_trailing_bytes_invalid_depth_stride_dimensions(self):
        for data, width, height, seed, order, stride in [
            (b"", 1, 1, 0, "ARGB8", 4), (b"\0" * 5, 1, 1, 0, "ARGB8", 4),
            (b"\0" * 4, 1, 1, 0, "ARGB16", 4), (b"", 0, 1, 0, "ARGB8", 4),
            (b"", 4097, 1, 0, "ARGB8", 4), (b"", 1, 1, -1, "ARGB8", 4),
            (b"", 1, 1, 0x1000000, "ARGB8", 4),
            (b"\0" * 4, 1, 1, 0, "ARGB8", -4), (b"\0" * 4, 1, 1, 0, "ARGB8", 3)]:
            with self.assertRaises(ValueError): oracle.compare(data, width, height, seed, order, stride)


if __name__ == "__main__":
    unittest.main()
