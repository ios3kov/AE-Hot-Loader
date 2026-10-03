"""Offline executor evidence/refusal controls, never AE runtime proof."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('executor_review', ROOT /
    'experiments/ordinary_discovery/executor_file_review.py')
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


class ExecutorFileReviewTests(unittest.TestCase):
    def table(self):
        words=[0]+[(2<<51)|target for target in review.TABLE_TARGETS[1:]]
        fixups=''.join(' __DATA_CONST __const 0x%x rebase 0x%x\n' %
                      (review.TABLE_START+i*8,target) for i,target in enumerate(review.TABLE_TARGETS) if i)
        chains='pointer_format: 6 (DYLD_CHAINED_PTR_64_OFFSET)\n'
        return words,fixups,chains

    def test_original_vtable_proves_file_slot_identity_only(self):
        result=review.verify_table(*self.table())
        self.assertEqual(result['rebases'],14)
        self.assertEqual(result['claim'],'file-executor-table-not-live-ABI-or-host-barrier')
        self.assertEqual(result['slot_targets']['0x10'],'0x14da0')
        self.assertEqual(result['slot_targets']['0x48'],'0x15450')

    def test_refuse_wrong_table_target_header_bind_reserved_or_incomplete_fixups(self):
        words,fixups,chains=self.table()
        for index,delta in [(0,1),(3,4),(4,1<<63),(8,1<<36),(12,1<<44)]:
            bad=list(words);bad[index]^=delta
            with self.subTest(index=index),self.assertRaises(ValueError):
                review.verify_table(bad,fixups,chains)
        for bad in [fixups.splitlines()[0]+'\n',fixups+fixups.splitlines()[0]+'\n',
                    fixups.replace('rebase','bind',1),fixups.replace('0x39def0','0x39def4'),
                    fixups.replace('0x14da0','0x14da4')]:
            with self.subTest(bad=bad),self.assertRaises(ValueError): review.verify_table(words,bad,chains)
        for bad in ['',chains.replace('6','2'),chains+'pointer_format: 2 (DYLD_CHAINED_PTR_64)\n']:
            with self.assertRaises(ValueError): review.verify_table(words,fixups,bad)
        with self.assertRaises(ValueError): review.verify_table(words+[0],fixups,chains)

    def test_inventory_hash_and_metadata_drift_refused_for_both_original_images(self):
        for image,identity in review.IDENTITIES.items():
            bodies=[row for row in review.BODIES if row[0]==image]
            good={'nlist_symbols':identity[1],'string_bytes':identity[2],'text_symbols':identity[3],
                  'selected':{r[3]:{'body_sha256':r[4]} for r in bodies}}
            seen=[]
            def parser(raw,uuid,requested,*,partitions):
                seen.append((raw,uuid,requested,partitions));return good
            self.assertEqual(review.collect_symbols(b'owned parser input',image,parser),good)
            self.assertEqual(len(seen[0][2]),len(bodies))
            for row in bodies:
                spans=seen[0][3][row[3]];self.assertEqual(spans[0][0],row[1]);self.assertEqual(spans[-1][1],row[2])
                self.assertTrue(all(high-low<=4096 for low,high in spans))
            for field in ['nlist_symbols','string_bytes','text_symbols']:
                bad=dict(good);bad[field]+=1
                with self.assertRaises(ValueError): review.collect_symbols(b'x',image,lambda *a,**k:bad)
            bad=dict(good);bad['selected']=dict(good['selected']);bad['selected'][bodies[0][3]]={'body_sha256':'0'*64}
            with self.assertRaises(ValueError): review.collect_symbols(b'x',image,lambda *a,**k:bad)
        with self.assertRaises(ValueError): review.collect_symbols(b'x','unknown',lambda *a:None)

    def test_fixed_complete_body_groups_cover_twenty_four_bounded_windows(self):
        self.assertEqual(len(review.BODIES),23)
        self.assertEqual(len(review.WINDOWS),24)
        self.assertEqual(sum((r[2]-r[1])//4 for r in review.BODIES),5901)
        for image,start,end,name,byte_hash in review.BODIES:
            spans=[(r[1],r[2]) for r in review.WINDOWS.values() if r[0]==image and start<=r[1]<end]
            self.assertEqual(spans[0][0],start);self.assertEqual(spans[-1][1],end)
            self.assertEqual([a for a,b in spans[1:]],[b for a,b in spans[:-1]])
            self.assertEqual(len(byte_hash),64)
            self.assertTrue(all(0<b-a<=4096 and a%4==b%4==0 for a,b in spans))
        schedule=next(r for r in review.BODIES if r[1]==0x79438c)
        self.assertGreater(schedule[2]-schedule[1],4096)
        self.assertEqual(review.TABLE_START,0x39ded0)
        self.assertEqual(len(review.TABLE_TARGETS),15)

    def test_window_requires_exact_review_digest_and_rejects_unknown_scope(self):
        calls=[]
        def verify(text,start,end,expected):
            calls.append((text,start,end,expected));return (end-start)//4
        label=next(iter(review.WINDOWS));row=review.WINDOWS[label]
        result=review.verify_window('owned transcript',label,verify)
        self.assertEqual(calls,[('owned transcript',row[1],row[2],row[3])])
        self.assertEqual(result['claim'],'file-only-executor-not-host-admission-or-drain')
        with self.assertRaises(ValueError):review.verify_window('x','unknown',verify)
        def refused(*args):raise ValueError('changed full transcript')
        with self.assertRaises(ValueError):review.verify_window('x',label,refused)


if __name__=='__main__':unittest.main()
