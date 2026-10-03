"""Owned private-file inventory evidence; synthetic providers/process/known files."""
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'experiments/ordinary_discovery'))
import run_pica_inventory_probe as probe


class InventoryEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='aehl-inventory-evidence-');self.addCleanup(self.tmp.cleanup)
        self.control=Path(self.tmp.name).resolve()/'control';self.control.mkdir(mode=0o700)
        known=[dict(bundle='/owned/one.plugin',module='/owned/one.plugin/Contents/MacOS/one',sha='e'*64,
                    resource_sha='f'*64,match='owned.one'),
               dict(bundle='/owned/two.plugin',module='/owned/two.plugin/Contents/MacOS/two',sha='1'*64,
                    resource_sha='2'*64,match='owned.two')]
        self.r=dict(run_id='pica-inventory-'+'a'*32,source_commit='b'*40,build_id='inventory-'+'c'*12,
                    module_path='/owned/diagnostic',host_executable=str(probe.EXPECTED_HOST),binary_sha256='d'*64,
                    control_directory=str(self.control),activation_env={'AEHL_PICA_INVENTORY_TOKEN':'3'*32},known_effects=known)
        self.observed=dict(pid=123,start='456.789',executable=str(probe.EXPECTED_HOST))

    def write(self,name,data):
        p=self.control/(name+'.txt');p.write_bytes(data);p.chmod(0o600);return p

    def journal(self,name,data=b''):
        d=dict(schema='PICA-JOURNAL-1',run=self.r['run_id'],source=self.r['source_commit'],build=self.r['build_id'],
               pid='123',start='456.789',module_hex=self.r['module_path'].encode().hex(),binary_sha256=self.r['binary_sha256'],
               phase=name,data_hex=data.hex())
        return self.write(name,''.join(k+'='+v+'\n' for k,v in d.items()).encode())

    def plugin(self,path='/owned/one.plugin',file_error=0,path_error=0,adapter_error=0):
        return dict(file_error=str(file_error),path_error=str(path_error),path_hex=path.encode().hex(),
          adapter_error=str(adapter_error),name_error='0',version_error='0',
          adapter_name_hex='' if adapter_error else b'owned-synthetic-adapter'.hex(),adapter_version='1')

    def fixture(self,plugins=None):
        if plugins is None:plugins=[self.plugin()]
        self.journal('claim',probe.request(self.r,self.observed))
        native=f"123:456.789:{self.r['host_executable']}:{self.r['module_path']}:{self.r['binary_sha256']}".encode()
        registry=b'owned.one\nowned.two\n'
        baseline=b'\n'.join(x.hex().encode() for x in (native,b'25.6x101:blank-clean-idle:1',registry))
        for name in ('before','after'):self.journal(name,baseline)
        known=''.join(k['module'].encode().hex()+','+k['sha']+','+k['resource_sha']+','+k['match'].encode().hex()+'\n' for k in self.r['known_effects']).encode()
        for name in ('known-before','known-after'):self.journal(name,known)
        for name in ('before-started','after-started','iterator-started','iterator-delete-started','iterator-deleted'):
            self.journal(name)
        lines=['schema=PICA-INVENTORY-1','status=COMPLETE','stage=complete','reason_hex=','suite_count=2']
        for i,(name,version) in enumerate(probe.SPECS):
            lines += ['suite_name_hex='+name.encode().hex(),'suite_version='+str(version),'acquire_error=0','provider_present=1']
            self.journal('acquire-started-'+str(i));self.journal('acquire-finished-'+str(i))
        lines += ['enumeration_complete=1','plugin_count='+str(len(plugins))]
        for i,p in enumerate(plugins):
            data=''.join(k+'='+v+'\n' for k,v in p.items()).encode();lines += data.decode().splitlines()
            self.journal('next-started-'+str(i));self.journal('next-finished-'+str(i),data)
        self.journal('next-started-'+str(len(plugins)))
        terminal=('\n'.join(lines)+'\n').encode();self.write('terminal',terminal);self.journal('result',terminal)
        image=b'/owned/synthetic/image'.hex().encode()+b',123,0\n'
        self.write('images-0',image);self.write('images-1',image)

    def alter(self,old,new):
        data=(self.control/'terminal.txt').read_bytes().replace(old,new);self.write('terminal',data);self.journal('result',data)

    def test_exact_bundle_and_module_correlation_no_publication_claim(self):
        self.fixture([self.plugin(),self.plugin('/owned/two.plugin/Contents/MacOS/two')]);r=probe.verify(self.r,self.observed)
        self.assertEqual([x['state'] for x in r['known_effects']],['LISTED','LISTED'])
        self.assertEqual(r['ordinary_effect_registration'],'NOT RUN');self.assertEqual(r['apply_render'],'NOT RUN')
        self.assertEqual(r['evidence_sha256']['terminal.txt'],hashlib.sha256((self.control/'terminal.txt').read_bytes()).hexdigest())

    def test_complete_known_file_not_listed(self):
        self.fixture([self.plugin('/owned/other.plugin')]);r=probe.verify(self.r,self.observed)
        self.assertEqual([x['state'] for x in r['known_effects']],['NOT_LISTED','NOT_LISTED'])

    def test_empty_complete_list_is_only_observed_not_listed(self):
        self.fixture([]);r=probe.verify(self.r,self.observed);self.assertEqual(r['plugins'],[])
        self.assertEqual(r['known_effects'][0]['state'],'NOT_LISTED')

    def test_unresolved_file_cannot_prove_absence(self):
        self.fixture([self.plugin(),self.plugin('',file_error=-1)]);r=probe.verify(self.r,self.observed)
        self.assertEqual([x['state'] for x in r['known_effects']],['LISTED','UNKNOWN'])

    def test_conversion_error_preserved_unknown(self):
        self.fixture([self.plugin('',path_error=-43)]);r=probe.verify(self.r,self.observed)
        self.assertEqual(r['plugins'][0]['path_error'],-43);self.assertEqual(r['known_effects'][0]['state'],'UNKNOWN')

    def test_adapter_error_does_not_erase_exact_file_presence(self):
        self.fixture([self.plugin(adapter_error=-2)]);r=probe.verify(self.r,self.observed)
        self.assertEqual(r['known_effects'][0]['state'],'LISTED');self.assertEqual(r['plugins'][0]['adapter_name_hex'],'')

    def test_basename_prefix_and_child_path_do_not_correlate(self):
        self.fixture([self.plugin('/elsewhere/one.plugin'),self.plugin('/owned/one.plugin.other'),self.plugin('/owned/one.plugin/arbitrary')])
        self.assertEqual(probe.verify(self.r,self.observed)['known_effects'][0]['state'],'NOT_LISTED')

    def test_duplicate_file_records_are_retained_not_deduplicated(self):
        self.fixture([self.plugin(),self.plugin()]);r=probe.verify(self.r,self.observed)
        self.assertEqual(r['known_effects'][0]['entry_indices'],[0,1])

    def test_entry_delta_mismatch_refused(self):
        self.fixture();self.journal('next-finished-0',b'changed')
        with self.assertRaises(ValueError):probe.verify(self.r,self.observed)

    def test_missing_null_end_stage_refused(self):
        self.fixture();(self.control/'next-started-1.txt').unlink()
        with self.assertRaises(OSError):probe.verify(self.r,self.observed)

    def test_known_file_or_baseline_change_refused(self):
        self.fixture();self.journal('known-after',b'changed')
        with self.assertRaises(ValueError):probe.verify(self.r,self.observed)

    def test_identity_tamper_and_duplicate_journal_field_refused(self):
        self.fixture();p=self.control/'before.txt';raw=p.read_bytes()
        for bad in (raw.replace(b'pid=123',b'pid=124'),raw+b'source='+b'b'*40+b'\n'):
            self.write('before',bad)
            with self.assertRaises(ValueError):probe.verify(self.r,self.observed)

    def test_invalid_count_and_partial_terminal_refused(self):
        self.fixture();self.alter(b'plugin_count=1',b'plugin_count=2049')
        with self.assertRaises(ValueError):probe.verify(self.r,self.observed)
        self.write('terminal',b'schema=PICA-INVENTORY-1\nstatus=STOPPED\n')
        with self.assertRaises(ValueError):probe.verify(self.r,self.observed)

    def test_invalid_getter_error_pointer_contract_refused(self):
        self.fixture([self.plugin('',file_error=0,path_error=0)])
        with self.assertRaises(ValueError):probe.verify(self.r,self.observed)

    def test_removed_image_refused(self):
        self.fixture();self.write('images-1',b'/owned/new'.hex().encode()+b',124,0\n')
        with self.assertRaises(ValueError):probe.verify(self.r,self.observed)

    def test_external_timeout_publishes_once_preserves_partial_without_retry(self):
        calls=[];times=iter([0,0,31])
        def publish(control,request):
            calls.append(request);self.write('request',request);self.journal('claim',request)
        result=probe.supervise(self.r,self.observed,publish_fn=publish,clock=lambda:next(times),sleep=lambda _:None)
        self.assertEqual(result['status'],'TIMEOUT');self.assertEqual(len(calls),1)
        self.assertTrue((self.control/'claim.txt').exists())
        self.assertFalse((self.control/'terminal.txt').exists())

    def test_live_cli_without_scope_denies_before_manifest_or_request(self):
        args=['probe','--manifest','not-opened','--manifest-sha256','0'*64,'--expected-bundle','not-opened']
        with patch.object(sys,'argv',args),patch.object(probe,'manifest') as read,patch.object(sys,'stderr'):
            with self.assertRaises(SystemExit) as e:probe.main()
            self.assertEqual(e.exception.code,2);read.assert_not_called()
        self.assertFalse((self.control/'request.txt').exists())

    def test_manifest_digest_duplicate_json_refused_before_runtime(self):
        p=self.write('manifest',b'{"kind":"fake","kind":"changed"}')
        with self.assertRaisesRegex(ValueError,'hash changed'):probe.manifest(p,'0'*64)
        with self.assertRaisesRegex(ValueError,'duplicate JSON'):
            probe.manifest(p,hashlib.sha256(p.read_bytes()).hexdigest())
