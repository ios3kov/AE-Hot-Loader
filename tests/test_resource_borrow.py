"""Observable refusal before access, and stale/short-read refusal after access."""
from pathlib import Path
import sys
import unittest
from types import SimpleNamespace
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from experiments.resource_trace.borrow import read, extent


class Error:
    def __init__(self, success=True): self.success = success
    def Success(self): return self.success


class Region:
    def IsMapped(self): return self.mapped
    def IsReadable(self): return self.readable
    def IsExecutable(self): return self.executable
    def GetRegionBase(self): return self.base
    def GetRegionEnd(self): return self.end


API = SimpleNamespace(eStateStopped=5, SBMemoryRegionInfo=Region, SBError=Error)


class Process:
    def __init__(self):
        self.stop = 4; self.state = 5; self.reads = 0; self.queries = 0
        self.mapping = (True, True, False, 1000, 2000)
        self.query_success = True; self.short = False; self.read_error = False
        self.resume_on_read = False; self.change_mapping = False
    def GetState(self): return self.state
    def GetStopID(self): return self.stop
    def GetMemoryRegionInfo(self, address, region):
        self.queries += 1
        region.mapped, region.readable, region.executable, region.base, region.end = self.mapping
        if self.change_mapping and self.queries == 2: region.end += 1
        return Error(self.query_success)
    def ReadMemory(self, address, size, error):
        self.reads += 1; error.success = not self.read_error
        if self.resume_on_read: self.stop += 1
        return b'x' * (size - int(self.short))


class BorrowTests(unittest.TestCase):
    def setUp(self): self.process = Process(); self.identities = 0
    def identity(self): self.identities += 1
    def run_read(self): return read(self.process, API, self.identity, 4, 1100, 20, 1090, 40)
    def test_copy_and_receipt_cover_exact_backing(self):
        raw, receipt = self.run_read()
        self.assertEqual(raw, b'x' * 20); self.assertEqual(self.process.reads, 1)
        self.assertEqual(self.identities, 4)
        self.assertEqual(receipt['backing_length'], 40)
        self.assertEqual(receipt['lifetime'], 'OWNED_FIXTURE_CALL_SCOPE_ONLY')
    def test_negative_null_boolean_overflow_and_large_extent(self):
        for args in ((0, 1, 1, 1), (True, 1, 1, 1), (1, 4097, 1, 4097),
                     (2**64-2, 2, 2**64-2, 2), (100, 10, 105, 10), (100, 11, 100, 10)):
            with self.subTest(args=args), self.assertRaises(ValueError): extent(*args)
    def test_bad_span_performs_no_mapping_or_read(self):
        with self.assertRaises(ValueError): read(self.process, API, self.identity, 4, 1100, 21, 1100, 20)
        self.assertEqual((self.process.queries, self.process.reads), (0, 0))
    def test_foreign_identity_refuses_before_mapping(self):
        def foreign(): raise ValueError('PID birth changed')
        with self.assertRaises(ValueError): read(self.process, API, foreign, 4, 1100, 20, 1100, 20)
        self.assertEqual((self.process.queries, self.process.reads), (0, 0))
    def test_stale_stop_refuses_before_mapping(self):
        self.process.stop = 5
        with self.assertRaises(ValueError): self.run_read()
        self.assertEqual(self.process.reads, 0)
    def test_running_refuses_before_mapping(self):
        self.process.state = 6
        with self.assertRaises(ValueError): self.run_read()
        self.assertEqual(self.process.reads, 0)
    def test_unmapped_unreadable_executable_or_crossing_extent(self):
        for mapping in ((False, True, False, 1000, 2000), (True, False, False, 1000, 2000),
                        (True, True, True, 1000, 2000), (True, True, False, 1100, 1110)):
            with self.subTest(mapping=mapping):
                self.process = Process(); self.process.mapping = mapping
                with self.assertRaises(ValueError): self.run_read()
                self.assertEqual(self.process.reads, 0)
    def test_mapping_query_failure_refuses_before_read(self):
        self.process.query_success = False
        with self.assertRaises(ValueError): self.run_read()
        self.assertEqual(self.process.reads, 0)
    def test_short_read_refuses(self):
        self.process.short = True
        with self.assertRaisesRegex(ValueError, 'short read'): self.run_read()
    def test_read_error_refuses(self):
        self.process.read_error = True
        with self.assertRaisesRegex(ValueError, 'short read'): self.run_read()
    def test_stop_changed_after_read_refuses(self):
        self.process.resume_on_read = True
        with self.assertRaisesRegex(ValueError, 'stop changed'): self.run_read()
    def test_mapping_changed_after_read_refuses(self):
        self.process.change_mapping = True
        with self.assertRaisesRegex(ValueError, 'mapping changed'): self.run_read()


if __name__ == '__main__': unittest.main()
