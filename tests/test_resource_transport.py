"""Negative controls cannot pass because of an unrelated debugger refusal."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from experiments.resource_trace.debug_fixture import verify_control


class TransportOracleTests(unittest.TestCase):
    def test_unrelated_refusal_does_not_pass_any_negative(self):
        row = {'status': 'REFUSED_OR_INCOMPLETE', 'cleanup_safe': True, 'process_absence': 'PASS',
               'debugger_exit_code': 0, 'stops': 1, 'reads': [], 'reason': 'not exactly one isolated breakpoint stop'}
        for fault in ('alias', 'writer-failure', 'wrong-owner', 'read-name', 'cross-reader', 'aba'):
            with self.subTest(fault=fault), self.assertRaisesRegex(ValueError, 'not observed'): verify_control(row, fault)
        with self.assertRaisesRegex(ValueError, 'not observed'): verify_control(row, bad_extent=True)
    def test_correct_aba_refusal_requires_observed_generation_boundary(self):
        row = {'status': 'REFUSED_OR_INCOMPLETE', 'cleanup_safe': True, 'process_absence': 'PASS',
               'debugger_exit_code': 0, 'stops': 9, 'reads': [None]*9,
               'reason': 'object/owner continuity differs', 'trace': {'status': 'REFUSED', 'accepted_events': 8}}
        verify_control(row, 'aba')
        row['trace']['accepted_events'] = 7
        with self.assertRaises(ValueError): verify_control(row, 'aba')
    def test_unsafe_cleanup_prevents_even_expected_refusal(self):
        with self.assertRaisesRegex(ValueError, 'lifecycle'): verify_control({'cleanup_safe': False}, bad_extent=True)
    def test_positive_requires_all_reads_and_stops(self):
        row = {'status': 'OWNED_RESOURCE_TRANSPORT_OBSERVED', 'cleanup_safe': True, 'process_absence': 'PASS',
               'debugger_exit_code': 0, 'stops': 10, 'reads': [None]*10, 'trace': {'status': 'FIXTURE_CHAIN_OBSERVED'}}
        verify_control(row)
        row['reads'].pop()
        with self.assertRaises(ValueError): verify_control(row)


if __name__ == '__main__': unittest.main()
