"""Real private files, synthetic host/provider data. Never observes or launches AE."""
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
LOCATION = ROOT / 'experiments/ordinary_discovery'
# Keep imports local and deterministic without executing any live entry point.
sys.path.insert(0, str(LOCATION))
import run_pica_availability_probe as probe


class PicaEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='aehl-pica-evidence-')
        self.addCleanup(self.tmp.cleanup)
        self.control = Path(self.tmp.name).resolve() / 'control'
        self.control.mkdir(mode=0o700)
        self.r = dict(run_id='pica-availability-'+'a'*32, source_commit='b'*40,
                      build_id='pica-'+'c'*12, module_path='/owned/synthetic/module',
                      host_executable=str(probe.EXPECTED_HOST), binary_sha256='d'*64,
                      control_directory=str(self.control),
                      activation_env={'AEHL_PICA_AVAILABILITY_TOKEN':'e'*32})
        self.observed = dict(pid=123, start='456.789', executable=str(probe.EXPECTED_HOST))

    def write(self, name, data):
        path = self.control / (name+'.txt')
        path.write_bytes(data);path.chmod(0o600)
        return path

    def journal(self, name, data=b''):
        d = dict(schema='PICA-JOURNAL-1',run=self.r['run_id'],source=self.r['source_commit'],
                 build=self.r['build_id'],pid='123',start='456.789',module_hex=self.r['module_path'].encode().hex(),
                 binary_sha256=self.r['binary_sha256'],phase=name,data_hex=data.hex())
        return self.write(name,''.join(k+'='+v+'\n' for k,v in d.items()).encode())

    def fixture(self, providers=True):
        self.journal('claim',probe.request(self.r,self.observed))
        native = (f"123:456.789:{self.r['host_executable']}:{self.r['module_path']}:{self.r['binary_sha256']}").encode()
        baseline = b'\n'.join(x.hex().encode() for x in (native,b'25.6x101:blank-clean-idle:1',b'owned-fixture\n'))
        for name in ('before','after'):self.journal(name,baseline)
        for name in ('before-started','after-started'):self.journal(name)
        lines=['schema=PICA-AVAILABILITY-1','status=COMPLETE','stage=complete','reason_hex=','suite_count=4']
        for i,(name,version) in enumerate(probe.SPECS):
            self.journal('acquire-started-'+str(i));self.journal('acquire-finished-'+str(i))
            lines += ['suite_name_hex='+name.encode().hex(),'suite_version='+str(version),
                      'acquire_error='+('0' if providers else '-3'),'provider_present='+('1' if providers else '0')]
        lines += ['enumeration_complete='+('1' if providers else '0'),'adapter_count='+('1' if providers else '0')]
        if providers:
            lines += ['adapter_name_hex='+b'owned-synthetic-adapter'.hex(),'adapter_version=3']
            for name in ('iterator-started','iterator-delete-started','iterator-deleted','next-started-0',
                         'next-finished-0','next-started-1'):self.journal(name)
        terminal=('\n'.join(lines)+'\n').encode()
        self.write('terminal',terminal);self.journal('result',terminal)
        image=b'/owned/synthetic/image'.hex().encode()+b',123,0\n'
        self.write('images-0',image);self.write('images-1',image)
        return terminal

    def replace_terminal(self, old, new):
        data=(self.control/'terminal.txt').read_bytes().replace(old,new)
        self.write('terminal',data);self.journal('result',data)

    def test_complete_reports_only_availability(self):
        self.fixture();result=probe.verify(self.r,self.observed)
        self.assertEqual(result['status'],'COMPLETE')
        self.assertEqual(result['ordinary_effect_registration'],'NOT RUN')
        self.assertEqual(result['apply_render'],'NOT RUN')
        self.assertEqual(len(result['adapters']),1)
        self.assertEqual(result['evidence_sha256']['terminal.txt'],hashlib.sha256((self.control/'terminal.txt').read_bytes()).hexdigest())

    def test_acquisition_errors_retained_without_absence_claim(self):
        self.fixture(False);result=probe.verify(self.r,self.observed)
        self.assertEqual([s['error'] for s in result['suites']],[-3]*4)
        self.assertEqual(result['adapters'],[])

    def test_missing_durable_stage_refused(self):
        self.fixture();(self.control/'acquire-started-2.txt').unlink()
        with self.assertRaises(OSError):probe.verify(self.r,self.observed)

    def test_changed_source_pid_start_and_hash_refused(self):
        self.fixture();path=self.control/'before.txt';original=path.read_bytes()
        for old,new in [(b'source='+b'b'*40,b'source='+b'f'*40),(b'pid=123',b'pid=124'),
                        (b'start=456.789',b'start=456.790'),(b'binary_sha256='+b'd'*64,b'binary_sha256='+b'f'*64)]:
            with self.subTest(old=old):
                self.write('before',original.replace(old,new))
                with self.assertRaises(ValueError):probe.verify(self.r,self.observed)
        self.write('before',original)

    def test_duplicate_journal_fields_refused(self):
        self.fixture();p=self.control/'claim.txt';self.write('claim',p.read_bytes()+b'pid=123\n')
        with self.assertRaises(ValueError):probe.verify(self.r,self.observed)

    def test_changed_project_or_registry_refused(self):
        self.fixture();self.journal('after',b'changed'.hex().encode()+b'\n'+b'changed'.hex().encode()+b'\n'+b'changed'.hex().encode())
        with self.assertRaises(ValueError):probe.verify(self.r,self.observed)

    def test_suite_error_pointer_contradiction_refused(self):
        self.fixture();self.replace_terminal(b'acquire_error=0',b'acquire_error=1')
        with self.assertRaises(ValueError):probe.verify(self.r,self.observed)

    def test_adapter_without_available_provider_refused(self):
        self.fixture();self.replace_terminal(b'suite_version=3\nacquire_error=0\nprovider_present=1\nenumeration_complete=1',
                                              b'suite_version=3\nacquire_error=1\nprovider_present=0\nenumeration_complete=0')
        with self.assertRaises(ValueError):probe.verify(self.r,self.observed)

    def test_invalid_adapter_version_and_trailing_fields_refused(self):
        for replacement in (b'adapter_version=2147483648',b'adapter_version=3\nunknown=1'):
            self.fixture();self.replace_terminal(b'adapter_version=3',replacement)
            with self.subTest(replacement=replacement),self.assertRaises(ValueError):probe.verify(self.r,self.observed)

    def test_potential_load_allowed_but_removed_image_refused(self):
        self.fixture();image=(self.control/'images-1.txt').read_bytes()
        self.write('images-1',image+b'/owned/synthetic/addition'.hex().encode()+b',124,0\n')
        self.assertEqual(len(probe.verify(self.r,self.observed)['added_image_paths_hex']),1)
        self.write('images-1',b'/owned/synthetic/addition'.hex().encode()+b',124,0\n')
        with self.assertRaises(ValueError):probe.verify(self.r,self.observed)

    def test_partial_timeout_result_not_complete(self):
        self.fixture();self.write('terminal',b'schema=PICA-AVAILABILITY-1\nstatus=STOPPED\n')
        with self.assertRaises(ValueError):probe.verify(self.r,self.observed)

    def test_private_file_symlink_hardlink_permissions_refused(self):
        p=self.write('file',b'owned');p.chmod(0o644)
        with self.assertRaises(ValueError):probe.private_read(p)
        p.chmod(0o600);os.link(p,self.control/'hard.txt')
        with self.assertRaises(ValueError):probe.private_read(p)
        (self.control/'hard.txt').unlink();(self.control/'link.txt').symlink_to(p)
        with self.assertRaises(ValueError):probe.private_read(self.control/'link.txt')

    def test_consumed_request_publication_never_overwrites(self):
        body=probe.request(self.r,self.observed)
        if sys.platform == 'darwin':
            probe.common.publish(self.control,body)
            with self.assertRaises(OSError):probe.common.publish(self.control,b'replacement')
        else:
            # Synthetic macOS transport on Linux CI, with real exclusive files.
            class Function:
                def __call__(self, source, destination, flag):
                    try:
                        os.link(source,destination);os.unlink(source);return 0
                    except FileExistsError:return -1
            class Library:renamex_np=Function()
            with patch.object(probe.common.ctypes,'CDLL',return_value=Library()):
                probe.common.publish(self.control,body)
                with self.assertRaises(OSError):probe.common.publish(self.control,b'replacement')
        self.assertEqual((self.control/'request.txt').read_bytes(),body)
        self.assertEqual({p.name for p in self.control.iterdir()},{'request.txt'})

    def test_readiness_binding_and_stale_control_before_request(self):
        self.r.update(source_clean=True,target='aarch64-apple-darwin',kind='research-only-pica-availability-aegp',
                      prospective_bundle='/owned/synthetic/bundle',files={'owned':'synthetic'})
        identity={k:self.r[k] for k in ('build_id','run_id','source_commit','source_clean','target','kind')}
        self.write('ready',(json.dumps(identity)+'\npid=123\nstart=456.789\nmodule_hex='+self.r['module_path'].encode().hex()+'\n').encode())
        with patch.object(probe.common,'bundle_hashes',return_value=self.r['files']), \
             patch.object(probe.common,'sha_trusted_binary',return_value=probe.HOST_SHA):
            observed,body=probe.prepare(self.r,self.r['prospective_bundle'],identity_fn=lambda _:self.observed)
            self.assertEqual(body,probe.request(self.r,observed))
            with self.assertRaises(ValueError):
                probe.prepare(self.r,self.r['prospective_bundle'],identity_fn=lambda _:dict(self.observed,start='456.790'))
            self.write('request',body)
            with self.assertRaises(ValueError):
                probe.prepare(self.r,self.r['prospective_bundle'],identity_fn=lambda _:self.observed)

    def test_manifest_digest_and_duplicate_keys_fail_before_runtime(self):
        path=self.write('manifest',b'{"kind":"synthetic","kind":"changed"}')
        with self.assertRaisesRegex(ValueError,'manifest hash changed'):probe.manifest(path,'0'*64)
        with self.assertRaisesRegex(ValueError,'duplicate JSON key'):
            probe.manifest(path,hashlib.sha256(path.read_bytes()).hexdigest())
