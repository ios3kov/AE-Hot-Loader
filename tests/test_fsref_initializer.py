"""Return-window models and one actual own-process initializer control. Never AE."""
from pathlib import Path
import platform
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from experiments.resource_trace.fsref_initializer import ReturnWindow, run


class WindowTests(unittest.TestCase):
    def test_repeated_success_at_same_address_has_distinct_generation(self):
        window=ReturnWindow()
        for generation in (1,2,3):
            window.enter(generation,88); window.returned(generation,88,True)
            window.capture(generation,88); window.close(generation,88)
        self.assertEqual(window.last,3)

    def test_return_without_entry(self):
        with self.assertRaisesRegex(ValueError,'^MISSING_ENTRY$'):
            ReturnWindow().returned(1,88,True)

    def test_stale_successful_A_same_address(self):
        window=ReturnWindow(); window.enter(1,88); window.returned(1,88,True); window.close(1,88)
        window.enter(2,88); window.returned(2,88,True)
        with self.assertRaisesRegex(ValueError,'^STALE_INVOCATION$'): window.capture(1,88)
        with self.assertRaisesRegex(ValueError,'^TERMINAL_WINDOW$'): window.capture(2,88)

    def test_false_does_not_admit_old_valid_A_bytes(self):
        window=ReturnWindow(); window.enter(1,88); window.returned(1,88,False)
        with self.assertRaisesRegex(ValueError,'^CALL_FAILED$'): window.capture(1,88)

    def test_missing_normal_return(self):
        window=ReturnWindow(); window.enter(1,88)
        with self.assertRaisesRegex(ValueError,'^MISSING_NORMAL_RETURN$'): window.capture(1,88)

    def test_capture_after_close(self):
        window=ReturnWindow(); window.enter(1,88); window.returned(1,88,True); window.close(1,88)
        with self.assertRaisesRegex(ValueError,'^NO_ACTIVE_INVOCATION$'): window.capture(1,88)

    def test_duplicate_capture(self):
        window=ReturnWindow(); window.enter(1,88); window.returned(1,88,True); window.capture(1,88)
        with self.assertRaisesRegex(ValueError,'^ALREADY_CAPTURED$'): window.capture(1,88)

    def test_new_pointer_does_not_match_old_entry(self):
        window=ReturnWindow(); window.enter(1,88)
        with self.assertRaisesRegex(ValueError,'^STALE_INVOCATION$'): window.returned(1,96,True)

    def test_false_can_close_without_capture_and_later_success_is_valid(self):
        window=ReturnWindow(); window.enter(1,88); window.returned(1,88,False); window.close(1,88)
        window.enter(2,88); window.returned(2,88,True); window.capture(2,88)
        self.assertTrue(window.captured)


class NativeTests(unittest.TestCase):
    @unittest.skipUnless(platform.system()=='Darwin' and platform.machine()=='arm64','native macOS arm64')
    def test_real_initializer_patterns_and_return_reuse(self):
        folder=tempfile.mkdtemp(prefix='aehl-initializer-')
        try:
            result=run(Path(folder).resolve()/'control')
            self.assertEqual(result['status'],'OWNED_INITIALIZER_OBSERVED')
            self.assertEqual(result['observation']['matrix_calls'],40)
            self.assertEqual(len(result['comparisons']),43)
            self.assertEqual(len(result['ordered_comparisons']),86)
            self.assertEqual(len(result['observation']['model_refusals']),5)
            self.assertEqual(result['observation']['full_write_coverage'],'UNKNOWN')
            self.assertEqual(result['AE_capture'],'BLOCKED')
        except BaseException:
            print('Owned initializer failure evidence retained: '+folder,file=sys.stderr)
            raise
        else:
            shutil.rmtree(folder) # Only this newly created, completed own test directory.


if __name__=='__main__': unittest.main()
