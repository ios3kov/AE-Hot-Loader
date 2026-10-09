"""Clock changes and sleep affect evidence, never renew a consumed request."""
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('owned_request_timeline',Path(__file__).resolve().parents[1]/'experiments/startup_trace/timeline.py')
timeline=importlib.util.module_from_spec(spec);spec.loader.exec_module(timeline)


def sample(wall=1000000, active=1000000000, continuous=2000000000):
    return dict(zip(timeline.FIELDS,(wall,active//1000000,active,continuous,1,1)))


class TimelineTests(unittest.TestCase):
    def test_normal_delivery_and_active_delay(self):
        normal=timeline.compare(sample(),sample(1002000,3000000000,4000000000),1110)
        self.assertEqual(normal['deadline_window'],'WITHIN_BUDGET')
        self.assertFalse(normal['suspension_observed']);self.assertFalse(normal['wall_shift_observed'])
        delay=timeline.compare(sample(),sample(1180000,181000000000,182000000000),1110)
        self.assertEqual(delay['deadline_window'],'EXPIRED');self.assertEqual(delay['active_elapsed_ms'],180000)
        self.assertFalse(delay['suspension_observed']);self.assertFalse(delay['wall_shift_observed'])

    def test_sleep_consumes_wall_deadline_with_little_active_time(self):
        result=timeline.compare(sample(),sample(1180000,3000000000,182000000000),1110)
        self.assertEqual(result['deadline_window'],'EXPIRED')
        self.assertEqual(result['suspension_excess_ms'],178000)
        self.assertTrue(result['suspension_observed']);self.assertFalse(result['wall_shift_observed'])

    def test_forward_and_backward_wall_changes_remain_distinct(self):
        for wall,window in [(1180000,'EXPIRED'),(820000,'FUTURE_OUTSIDE_BUDGET')]:
            with self.subTest(wall=wall):
                result=timeline.compare(sample(),sample(wall,3000000000,4000000000),1110)
                self.assertEqual(result['deadline_window'],window)
                self.assertFalse(result['suspension_observed']);self.assertTrue(result['wall_shift_observed'])

    def test_invalid_numbers_domains_and_backward_elapsed_are_refused(self):
        for bad in [{**sample(),'timebase_denom':0},{**sample(),'wall_ms':True},
                    {**sample(),'absolute_ticks':-1},{**sample(),'extra':1}]:
            with self.assertRaises(ValueError):timeline.compare(sample(),bad,1110)
        for bad in [sample(active=0),{**sample(),'timebase_numer':2},sample(continuous=0)]:
            with self.assertRaises(ValueError):timeline.compare(sample(),bad,1110)

    def test_native_receipt_identity_and_strict_fields(self):
        raw=('AEHL-CAL-TIMING-1\nbuild=owned-build\npid=42\nbirth=99\nphase=2\ndeadline=1110\n'+
             ''.join(k+'='+str(v)+'\n' for k,v in sample().items())).encode()
        result=timeline.parse_native(raw,'owned-build',42,99,2)
        self.assertEqual(result['sample'],sample())
        for wrong in [raw.replace(b'pid=42',b'pid=43'),raw.replace(b'phase=2',b'phase=0'),
                      raw.replace(b'build=owned-build',b'build=other'),raw+b'wall_ms=1\n',
                      raw+b'extra=1\n',raw.replace(b'deadline=1110',b'deadline=-1'),
                      raw.replace(b'timebase_denom=1',b'timebase_denom=0')]:
            with self.assertRaises(ValueError):timeline.parse_native(wrong,'owned-build',42,99,2)

    def test_new_timing_source_is_pinned_in_collector_inventory(self):
        text=(Path(__file__).resolve().parents[1]/'experiments/startup_trace/profile.py').read_text()
        self.assertIn("'timeline.py'",text)
