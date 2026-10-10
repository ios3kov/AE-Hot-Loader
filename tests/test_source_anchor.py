"""Real kernel fd queries, dup2 twin, and same-inode byte mutation; owned only."""
from pathlib import Path
import platform
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from experiments.resource_trace.source_anchor import run


class SourceAnchorTests(unittest.TestCase):
    @unittest.skipUnless(platform.system() == 'Darwin' and platform.machine() == 'arm64', 'native macOS arm64 control')
    def test_kernel_source_and_intended_refusals(self):
        with tempfile.TemporaryDirectory(prefix='aehl-source-anchor-') as directory:
            result = run(Path(directory) / 'controls')
            self.assertEqual(len(result['controls']), 3)
            self.assertEqual(result['AE_run'], 'NOT_RUN')
            self.assertEqual(result['Adobe_buffer_lifetime'], 'UNKNOWN')


if __name__ == '__main__':
    unittest.main()
