"""Full collector flow under mocked inspection tools; never an AE runtime test."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import zipfile

SOURCE = Path(__file__).resolve().parents[1] / 'experiments/ordinary_discovery/collect_factory_image.py'
spec = importlib.util.spec_from_file_location('factory_flow_collect', SOURCE)
collect = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collect)


class CollectorFlowTests(unittest.TestCase):
    def exercise(self, mode, factory_only=False):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            app = base / 'app'
            image = app / (collect.IMAGE_PATHS['MEE'] if factory_only else collect.REL_IMAGE)
            image.parent.mkdir(parents=True)
            image.write_bytes(b'image')
            host = app / 'Contents/MacOS/After Effects'
            host.parent.mkdir()
            host.write_bytes(b'host')
            (base / 'Desktop').mkdir()
            seen = []

            def run(argv, folder, name, timeout=60):
                seen.append(argv)
                if mode == 'tool-error':
                    raise OSError('reader failed')
                output = (b'0000000000001000 (__TEXT,__text) external _AELibraryVideoFilterFactory_Create\n'
                          b'0000000000001010 (__TEXT,__text) external _other\n') if name == 'symbols.txt' else b'offline output\n'
                if name == 'disassembly.txt':
                    output = (b'(lldb) disassemble --start-address 0x1000 --end-address 0x1010\n'
                              b'fixture[0x1000] <+0>: mov w0, #7 ; "error: owned string"\n'
                              b'fixture[0x1004] <+4>: nop\nfixture[0x1008] <+8>: nop\n'
                              b'fixture[0x100c] <+12>: ret\n(lldb) quit\n')
                if name == 'disassembly.txt' and mode == 'diagnostic-error':
                    output += b'error: synthetic diagnostic\n'
                if name == 'disassembly.txt' and mode == 'empty-transcript':
                    output = b''
                if mode == 'no-matches' and name == 'symbols.txt':
                    output = b'0000000000001000 (__TEXT,__text) external _other\n'
                (folder / name).write_bytes(output)
                (folder / (name + '.stderr')).write_bytes(b'')
                if mode == 'image-change' and name == 'disassembly.txt':
                    image.write_bytes(b'changed')
                return output

            expected = '0' * 64 if mode == 'bad-host' else collect.digest(host)
            with mock.patch.object(collect.sys, 'platform', 'darwin'), \
                    mock.patch.object(collect, 'APP', app), \
                    mock.patch.object(collect, 'MAIN_SHA256', expected), \
                    mock.patch.object(collect, 'MEE_IMAGE_SHA256', '0' * 64 if mode == 'bad-image' else collect.digest(image)), \
                    mock.patch.object(Path, 'home', return_value=base), \
                    mock.patch.object(collect, 'run_tool', side_effect=run), \
                    contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()):
                status = collect.main('MEE', factory_only=True) if factory_only else collect.main()
            archives = list((base / 'Desktop').glob('*.zip'))
            if mode == 'good':
                self.assertEqual(status, 0)
                self.assertEqual(len(archives), 1)
                with zipfile.ZipFile(archives[0]) as archive:
                    record = json.loads(archive.read('record.json'))
                    self.assertEqual(record['capture_status'], 'PASS')
                    self.assertEqual(record['disassembly_validation']['windows'], 1)
                    self.assertEqual(record['factory_only'], factory_only)
                    self.assertEqual(record['runtime_registration'], 'NOT RUN')
                    self.assertEqual(record['current_project'], 'NOT OBSERVED')
                    self.assertEqual(record['image_before_sha256'], record['image_after_sha256'])
                    commands = archive.read('inspect.lldb').decode()
                    self.assertNotIn('process ', commands)
                    self.assertNotIn('expression ', commands)
                self.assertEqual(image.read_bytes(), b'image')
                self.assertEqual(host.read_bytes(), b'host')
            elif mode == 'no-matches':
                self.assertEqual(status, 2)
                self.assertEqual(len(archives), 1)
                self.assertFalse(any('lldb' in arg for argv in seen for arg in argv))
            else:
                self.assertEqual(status, 2)
                self.assertEqual(archives, [])

    def test_success(self):
        self.exercise('good')

    def test_no_matches(self):
        self.exercise('no-matches')

    def test_changed_main(self):
        self.exercise('bad-host')

    def test_changed_image(self):
        self.exercise('image-change')

    def test_tool_failure(self):
        self.exercise('tool-error')

    def test_real_diagnostic_line_blocks(self):
        self.exercise('diagnostic-error')

    def test_zero_exit_empty_output_blocks(self):
        self.exercise('empty-transcript')

    def test_factory_focus_success(self):
        self.exercise('good', factory_only=True)

    def test_factory_focus_image_hash_mismatch(self):
        self.exercise('bad-image', factory_only=True)


if __name__ == '__main__':
    unittest.main()
