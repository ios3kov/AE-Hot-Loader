import importlib.util
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest
import zlib

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('queue_live', ROOT/'experiments/startup_calibration/run.py')
live = importlib.util.module_from_spec(spec); spec.loader.exec_module(live)


def chunk(kind, data):
    return struct.pack('>I', len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)


def image(channels=4, filter_type=0, seed=0x345678):
    rgba=live.oracle.expected(64,48,seed,'RGBA8')
    rows=[bytes(v for x,v in enumerate(rgba[y*256:(y+1)*256]) if channels==4 or x%4!=3) for y in range(48)]
    encoded=bytearray();prior=bytes(64*channels)
    for row in rows:
        encoded.append(filter_type)
        for x,value in enumerate(row):
            left=row[x-channels] if x>=channels else 0
            up=prior[x];corner=prior[x-channels] if x>=channels else 0
            if filter_type==4:
                estimate=left+up-corner
                distances=[abs(estimate-v) for v in (left,up,corner)]
                predictor=(left,up,corner)[distances.index(min(distances))]
            else: predictor=(0,left,up,(left+up)//2)[filter_type] if filter_type<4 else 0
            encoded.append((value-predictor)%256)
        prior=row
    header=struct.pack('>IIBBBBB',64,48,8,6 if channels==4 else 2,0,0,0)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',header)+chunk(b'IDAT',zlib.compress(encoded))+chunk(b'IEND',b'')


class QueueControlTests(unittest.TestCase):
    def test_all_png_filters_rgb_rgba_match_independent_oracle(self):
        for channels in (3,4):
            for filter_type in range(5):
                pixels,metadata=live.png.decode(image(channels,filter_type))
                self.assertEqual(pixels,live.oracle.expected(64,48,0x345678,'RGBA8'))
                self.assertEqual(metadata['source_channels'],channels)

    def test_reject_corruption_truncation_trailing_duplicate_and_unknown_critical(self):
        good=image();bad=bytearray(good);bad[40]^=1
        for data in (bytes(bad),good[:-1],good+b'x',good[:8]+good[8:33]+good[8:],
                     good[:33]+chunk(b'ABCD',b'x')+good[33:],good[:33]+chunk(b'tRNS',b'\0'*6)+good[33:]):
            with self.assertRaises(ValueError):live.png.decode(data)

    def test_bounded_decompression_invalid_filter_depth_dimensions_and_stream(self):
        for width,depth,filter_type,raw in [(65,8,0,None),(64,16,0,None),(64,8,5,None),
                                           (64,8,0,b'x'*1000000),(64,8,0,b'x')]:
            header=struct.pack('>IIBBBBB',width,48,depth,6,0,0,0)
            pixels=raw if raw is not None else (bytes([filter_type])+b'\0'*256)*48
            data=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',header)+chunk(b'IDAT',zlib.compress(pixels))+chunk(b'IEND',b'')
            with self.assertRaises(ValueError):live.png.decode(data)

    def test_separate_queue_request_does_not_select_async(self):
        record={'token':'a'*32,'bundles':[{}, {'binary_sha256':'d'*64}]}
        observed={'pid':123,'start':'456.000007'}
        queue=live.request(record,observed,1000,True).decode().split()
        self.assertEqual(queue[5],'OWNED-STARTUP-QUEUE-CONTROL')
        self.assertEqual(live.request(record,observed,1000).decode().split()[5],'OWNED-STARTUP-APPLY-RENDER')

    def test_queue_completion_provenance_counter_and_pixels_are_separate(self):
        record={'build_id':'own-build','seed':0x345678}
        result=b'AEHL-CAL-RESULT-2\nbuild=own-build\nstatus=LISTED_APPLIED_QUEUE_EXPORTED\nrender=QUEUE_PIXEL_CHECK_PENDING\ncleanup=PASS\ncleanup_safe=YES\nkey=796\n'
        metadata=b'AEHL-CAL-QUEUE-FRAME-1\nbuild=own-build\nkey=796\ncounter_before=0\ncounter_after=1\nworking_space=NONE\nrevision=7\n'
        queue=b'AEHL-CAL-QUEUE-1\nstatus=DONE\nformat=PNG Sequence\nchannels=RGB + Alpha\nwidth=64\nheight=48\ntime=1/24\nduration=1/24\nrevision=7\n'
        self.assertEqual(live.verify_queue(record,result,metadata,queue,image())['pixels']['pixel_status'],'PASS')
        for r,m,q,p in [(result.replace(b'own-build',b'other'),metadata,queue,image()),
                        (result,metadata.replace(b'counter_after=1',b'counter_after=0'),queue,image()),
                        (result.replace(b'cleanup_safe=YES',b'cleanup_safe=NO'),metadata,queue,image()),
                        (result,metadata,queue.replace(b'DONE',b'USER_STOPPED'),image()),
                        (result,metadata,queue,image(seed=0x345679)),(result,metadata,queue,image(channels=3)),
                        (result,metadata.replace(b'revision=7',b'revision=8'),queue,image())]:
            with self.assertRaises(ValueError):live.verify_queue(record,r,m,q,p)

    def test_actual_generated_script_refusals_and_single_render(self):
        with tempfile.TemporaryDirectory(prefix='aehl-queue-script-') as directory:
            root=Path(directory);binary=root/'generate';script=root/'queue.jsx'
            compiler=shutil.which('clang++') or shutil.which('g++')
            self.assertIsNotNone(compiler)
            subprocess.run([compiler,'-std=c++17','-Wall','-Wextra','-Werror',str(ROOT/'tests/queue_script_source.cpp'),'-o',str(binary)],
                           check=True,capture_output=True,timeout=45)
            script.write_bytes(subprocess.run([str(binary)],check=True,capture_output=True,timeout=10).stdout)
            output=subprocess.run(['node',str(ROOT/'tests/startup_queue_script.mjs'),str(script)],
                                  check=True,capture_output=True,timeout=15)
            self.assertEqual(output.stdout,b'QUEUE_SCRIPT_CASES=27 PASS; model-only; Adobe_calls=0\n')
