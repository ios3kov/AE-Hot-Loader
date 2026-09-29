import importlib.util
from pathlib import Path
import struct
import unittest

spec = importlib.util.spec_from_file_location('pair', Path(__file__).resolve().parents[1] / 'experiments/ordinary_discovery/build_registration_pair.py')
pair = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pair)

class ResourcePairTests(unittest.TestCase):
    def test_variants(self):
        self.assertEqual(pair.variants('resource'), [(0,'Rsrc','rsrc'),(0,'Flat','flat')])
        self.assertEqual(pair.variants('dynamic'), [(0,'PiPL','rsrc'),(1,'Dynamic','rsrc')])
        with self.assertRaises(ValueError): pair.variants('unknown')

    def test_only_identities_differ(self):
        def properties(label):
            data=pair.pipl('AEHL '+label+' 0123456789ab','AEHL.'+label+'.0123456789ab')
            version,count=struct.unpack_from('>II',data)
            self.assertEqual(version,0)
            offset=8; result={}
            for _ in range(count):
                self.assertEqual(data[offset:offset+4],b'8BIM')
                key=data[offset+4:offset+8]
                ident,size=struct.unpack_from('>II',data,offset+8)
                self.assertEqual(ident,0)
                result[key]=data[offset+16:offset+16+size]
                offset+=16+((size+3)//4)*4
            self.assertEqual(offset,len(data))
            return result
        a,b=properties('Rsrc'),properties('Flat')
        self.assertEqual(set(a),set(b))
        self.assertEqual({k for k in a if a[k]!=b[k]}, {b'name',b'eMNA'})
        self.assertEqual(a[b'kind'],b'eFKT')
        self.assertEqual(a[b'ma64'],pair.pascal('EffectMain'))
