"""Fixed file-only suspend-context evidence and refusal controls."""
from pathlib import Path
import importlib.util
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('suspend_review', ROOT /
    'experiments/ordinary_discovery/suspend_file_review.py')
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)
parser_spec = importlib.util.spec_from_file_location('queue_parser', ROOT /
    'experiments/ordinary_discovery/workqueue_file_review.py')
parser = importlib.util.module_from_spec(parser_spec)
parser_spec.loader.exec_module(parser)


class SuspendFileReviewTests(unittest.TestCase):
    def test_original_inventory_or_complete_body_hash_drift_is_refused(self):
        good = {'nlist_symbols':14740,'string_bytes':308320,'text_symbols':2497,
                'selected':{r[3]:{'body_sha256':r[4]} for r in review.BODIES}}
        seen = []
        def accept(raw, uuid, requested):
            seen.append((raw,uuid,requested));return good
        self.assertEqual(review.collect_symbols(b'owned parser input',accept),good)
        self.assertEqual(seen[0][1],'3053ea7ea176315d900b9f17cc96dbe5')
        self.assertEqual(seen[0][2],{r[3]:(r[1],r[2]) for r in review.BODIES})
        for field in ['nlist_symbols','string_bytes','text_symbols']:
            bad = dict(good);bad[field]+=1
            with self.assertRaises(ValueError):review.collect_symbols(b'x',lambda *a:bad)
        bad = dict(good);bad['selected']=dict(good['selected'])
        bad['selected'][review.BODIES[0][3]]={'body_sha256':'0'*64}
        with self.assertRaises(ValueError):review.collect_symbols(b'x',lambda *a:bad)
        with self.assertRaises(ValueError):review.collect_symbols(b'x',lambda *a:{})

    def test_complete_fixed_original_scope_preserves_bounded_capture(self):
        self.assertEqual(len(review.BODIES),27)
        self.assertEqual(len(review.WINDOWS),27)
        self.assertEqual(sum((r[2]-r[1])//4 for r in review.BODIES),3788)
        self.assertEqual(len({r[3] for r in review.BODIES}),27)
        self.assertTrue(all(r[0]=='U' and 0<r[2]-r[1]<=4096 for r in review.BODIES))

    def test_exact_thunk_transcript_and_changed_instruction_refusal(self):
        text='U.dylib[0x164e0] <+0>: b 0x164e4\n'
        result=review.verify_window(text,'sus-U-164e0',parser.verify_transcript)
        self.assertEqual(result['decoded_instructions'],1)
        self.assertEqual(result['claim'],'file-only-context-transfer-not-host-admission-or-drain')
        for bad in [text.replace('164e4','164e8'),text+text,text.replace(' b ',' bl '),'']:
            with self.assertRaises(ValueError):review.verify_window(bad,'sus-U-164e0',parser.verify_transcript)
        with self.assertRaises(ValueError):review.verify_window(text,'unknown',parser.verify_transcript)

    def test_claims_never_promote_context_activation_or_callback_return_to_host_safety(self):
        claims=review.claims()
        self.assertEqual(claims['context_scope'],'CURRENT-TLS-CONTEXT-TRANSFER-NOT-GLOBAL-QUIESCENCE')
        self.assertEqual(claims['activation_token_scope'],'PER-CONTEXT-ACTIVATION-OWNERSHIP-NOT-REGISTRY-TRANSACTION')
        self.assertEqual(claims['terminate_scope'],'PROCESS-FLAG-NOT-ALL-JOB-JOIN')
        self.assertEqual(claims['supported_host_owner_thread_contract'],'UNKNOWN')
        self.assertEqual(claims['host_wide_reader_render_exclusion'],'NOT PROVEN')
        self.assertEqual(claims['whole_effect_rollback'],'NOT PROVEN')
        self.assertEqual(claims['native_experiment'],'BLOCKED')
        self.assertEqual(claims['registration_apply_render'],'NOT RUN')


if __name__=='__main__':unittest.main()
