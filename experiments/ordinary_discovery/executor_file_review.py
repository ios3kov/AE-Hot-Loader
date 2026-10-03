"""Fixed original executor evidence; no loader, process or callable host ABI."""
import re


def require(value, reason):
    if not value:
        raise ValueError(reason)


IDENTITIES = {
    'BEE': ('161300f373f83ebca751959df40a073b', 271537, 7871712, 58390),
    'dvacore': ('4427999d3db3396482f718df4fa24d76', 70803, 2366720, 12012),
}

# Complete bodies: image/start/next-defined-text end/name/original byte digest.
BODIES = (
    ('BEE', 0x7901b4, 0x790918,
     '__Z19BEE_WorkQueue_Birthji',
     'ab9eee2aa45418e4ad9e130a57cb8b91a618dbb02d10e26279ae0209e715ae5f'),
    ('BEE', 0x790f2c, 0x791170,
     '__Z19BEE_WorkQueue_Deathv',
     '4600382be1d20d233484d3d3e8e57b7e2f59994e9278d51e41c5d68ac6c127c4'),
    ('BEE', 0x79438c, 0x7953f0,
     '__ZL37BEEp_WorkQueue_Scheduler_ScheduleWorkRKN5boost10shared_ptrIN3bee14WorkQueue_ItemEEE17WorkQueuePriorityNSt3__110shared_ptrIN7dvacore7threads21AsyncThreadedExecutorEEE',
     'c5f72946084e67d2fc77ea479af51d2629bdc47e063340048a6c8811de8a81f4'),
    ('BEE', 0x7acde4, 0x7ad27c,
     '__ZL25WorkThread_ExecuteRoutineRKN5boost10shared_ptrIN3bee14WorkQueue_ItemEEERKNS_8functionIFvyEEE',
     '702d1268ce3f073e3c48ab09d77c57b7954a57e3bce0528809882ec2ad61f9d8'),
    ('BEE', 0x7b9cc8, 0x7ba0cc,
     '__ZL44BEEp_WorkQueue_Scheduler_WorkList_RemoveWorkRNSt3__14listIN5boost10shared_ptrI12WorkListNodeEENS_9allocatorIS4_EEEEy',
     'b571e8bf9b0087d832384db05c265dd6ccec71c9afb5c9991dd0855ed72b0d27'),
    ('BEE', 0x7e431c, 0x7e48cc,
     '__ZN3bee25BEEp_WorkQueue_ItemNotifyE14ItemChangeTypeRKN5boost10shared_ptrINS_14WorkQueue_ItemEEEb',
     'f2cd328fa622a7e5c305f8b43926fb12accffa7e8afba8d68c33dd14a2422eaa'),
    ('BEE', 0x7abcc4, 0x7ac64c,
     '__Z35BEE_WorkQueue_PostCompletionRoutineN5boost10shared_ptrI20BEE_WorkQueue_ClientEENS0_I19BEE_WorkQueueIdListEERKNS_8functionIFvyiEEE',
     '74b5f69f19fd072ff996cb85c6ce6b19c862d39a1aa2f93219282a251d1a8648'),
    ('dvacore', 0x139cc, 0x14564,
     '__ZN7dvacore7threads27CreateAsyncThreadedExecutorERKNSt3__112basic_stringIcNS1_11char_traitsIcEENS1_9allocatorIcEEEEiNS0_14ThreadPriorityERKNS1_8functionIFvvEEESF_RKNS0_16ThreadAttributesE',
     '9a2902543096f1f77545904b9ddbbc23b3c972bc581eebb0f68ae4353e06b4c2'),
    ('dvacore', 0x147d8, 0x14c30,
     '__ZN7dvacore7threads12_GLOBAL__N_117ThreadedWorkQueue10WorkerMainERKNSt3__110shared_ptrINS0_20ThreadSafeDelayQueueEEERKNS4_INS0_4GateEEERKNS4_INS3_5mutexEEERKNS4_INS3_6vectorImNS_9allocator12STLAllocatorImEEEEEE',
     '3e39528c30c6d46875e52714b51c276c8af213899bd47cbb691ec5fc94de969f'),
    ('dvacore', 0x14c30, 0x14d8c,
     '__ZN7dvacore7threads12_GLOBAL__N_117ThreadedWorkQueueD1Ev',
     '342c347ef9136a2000f65bcef884cd9e6d7d0143d8db125d826b161768c7306f'),
    ('dvacore', 0x14da0, 0x14ff4,
     '__ZN7dvacore7threads12_GLOBAL__N_117ThreadedWorkQueue18CallAsynchronouslyENSt3__18functionIFvvEEEj',
     'eee050a034148f55dece0befbcda68d604931ec45ac69d1cf6ca3c1d491d42d2'),
    ('dvacore', 0x15004, 0x15240,
     '__ZN7dvacore7threads12_GLOBAL__N_117ThreadedWorkQueue9TerminateEv',
     'ad785a134b1b63a618f30451d197323de86fe1e7be644c02887c9adf122e3022'),
    ('dvacore', 0x15450, 0x15b64,
     '__ZN7dvacore7threads12_GLOBAL__N_117ThreadedWorkQueue5FlushEv',
     'ff1f04f00359791132173f9ac0df33a16109b6b28ca8775e42f89b63ce50778d'),
    ('dvacore', 0x15b64, 0x15c70,
     '__ZN7dvacore7threads12_GLOBAL__N_117ThreadedWorkQueue5PauseEv',
     'd784586260e1da28029f5cd82d40c248a1bc3aa97fb0857175c76baf73a0528a'),
    ('dvacore', 0x15c70, 0x15d7c,
     '__ZN7dvacore7threads12_GLOBAL__N_117ThreadedWorkQueue6ResumeEv',
     'a3626ac5918cfe1e419083fdef052e9c755a30888db87d0429de5b22fc97759e'),
    ('dvacore', 0x15d7c, 0x15ea4,
     '__ZN7dvacore7threads12_GLOBAL__N_117ThreadedWorkQueue16BlockWhilePausedEv',
     '9d01f165041b37c1104bad3eeb459f73960d7d8b4b7b40798ebc49dcd983e6e8'),
    ('dvacore', 0x17bb0, 0x17dd4,
     '__ZN7dvacore7threads12_GLOBAL__N_117ThreadedWorkQueue4PushERKNSt3__110shared_ptrINS0_20ThreadSafeDelayQueueEEENS3_8functionIFvvEEEjb',
     'c86c6d31c081b9abbfb1b250b5a53164c1eeb88f0d8647cc801e692d2ae8237e'),
    ('dvacore', 0x18644, 0x1864c,
     '__ZNSt3__110__function6__funcIZN7dvacore7threads12_GLOBAL__N_117ThreadedWorkQueue5FlushEvEUlvE_NS_9allocatorIS6_EEFvvEEclEv',
     'bf3018eda36c55066303b765f0a36024c3763de9320e028de2633e8e15840a29'),
    ('BEE', 0x78f8b0, 0x78fb6c,
     '__ZN30BEE_WorkQueue_ItemStage_ScoperC2ERKN5boost10shared_ptrIN3bee14WorkQueue_ItemEEE',
     'bdbf594fa772ed08761f3db04289942d43df2f710e335e00b40e813edb7ed2aa'),
    ('BEE', 0x78fc28, 0x78fe90,
     '__ZN30BEE_WorkQueue_ItemStage_ScoperD2Ev',
     'f49d44c429ad1ce0aee45a39cfb54a65d651379fc35540a64bb1eef91bafbbf5'),
    ('BEE', 0x7ac64c, 0x7ac8a4,
     '__ZL32WorkThread_PostCompletionRoutineRKN5boost10shared_ptrIN3bee14WorkQueue_ItemEEERKNS_8functionIFvyiEEE',
     'dbfe76589fe5be8bd7831dc2f2a608f767864eeb8b71094424cc4b7708d3c5e3'),
    ('dvacore', 0x243bbc, 0x243c24,
     '__ZN7dvacore7threads4Gate4OpenEv',
     'd2fe4c49c10c28fa2364a2aedf7b9e68c3d0fe229fbd20bc5ec544c7bbafc085'),
    ('dvacore', 0x243c24, 0x243c38,
     '__ZN7dvacore7threads4Gate5CloseEv',
     '5c2931af42f4cf765e04c54c460c8d163a6a83db112c6a0e886545cbbb6fb90e'),
)

# Each capture stays <=4096 bytes; large bodies require all contiguous windows.
WINDOWS = {
    'exe-BEE-7901b4': ('BEE', 0x7901b4, 0x790918,
        '6500c5faba9ab64f88267d497094ca422c5999271bdb8c2677ae40850424ed89'),
    'exe-BEE-790f2c': ('BEE', 0x790f2c, 0x791170,
        '635c765a0d39cd4f67718f79a77cf5161973df944c7431b092f337dcb9c3cec7'),
    'exe-BEE-79438c': ('BEE', 0x79438c, 0x79538c,
        'fd0fc82643737456e3b6fc4841a00a59312b6237d4281b0e9b11e5ceff829fc7'),
    'exe-BEE-79538c': ('BEE', 0x79538c, 0x7953f0,
        '4f1bcf13b60314f340e42dd085f7481a06e5b7cb276dbd8451815cabf6e6f5f2'),
    'exe-BEE-7acde4': ('BEE', 0x7acde4, 0x7ad27c,
        '8d80aa000249b1b7e68b5a24469428a6ac68abf219b89c8f220772ca6f397ee2'),
    'exe-BEE-7b9cc8': ('BEE', 0x7b9cc8, 0x7ba0cc,
        'f996a9d2996280f7cc4b550056b923e8e04dc0395b983a3fad91e626e150e048'),
    'exe-BEE-7e431c': ('BEE', 0x7e431c, 0x7e48cc,
        'b0e3a1315be2abd58f9c8c6dc018f0566f8ce9d16fae5cbf6416a475c8807a10'),
    'exe-BEE-7abcc4': ('BEE', 0x7abcc4, 0x7ac64c,
        'b08920cd584060d69b30a16c340508af758018868981abe1326e5d4e076beb55'),
    'exe-BEE-78f8b0': ('BEE', 0x78f8b0, 0x78fb6c,
        '208d4d9930b336bf4de58818651249b2f28780e66f791cb2184d57c2f3fcd6b5'),
    'exe-BEE-78fc28': ('BEE', 0x78fc28, 0x78fe90,
        'c3d18c31706904923801d2015575c5a0c60510c6111a54055569df0098387f61'),
    'exe-BEE-7ac64c': ('BEE', 0x7ac64c, 0x7ac8a4,
        '7c8257ed90afb7d3acc380678a472dcc8c9ffafc1373a4256827dc0ad694b8ba'),
    'exe-dvacore-139cc': ('dvacore', 0x139cc, 0x14564,
        '90c8b0c6bcf06477ab9880dcdb05a02b022c932383f244dc0ef365ca25811433'),
    'exe-dvacore-147d8': ('dvacore', 0x147d8, 0x14c30,
        'eafa52d6b7e091d2633f1d95fb2c4046c4a6b8f84bd3641c9a65b877eac9faca'),
    'exe-dvacore-14c30': ('dvacore', 0x14c30, 0x14d8c,
        '84c4be3030a3252e076abeb37abcf8dc7b1b17a288a1f5ed5cbef850ecb30df2'),
    'exe-dvacore-14da0': ('dvacore', 0x14da0, 0x14ff4,
        '1097c7d25181921e97a208eb58eb00e33695d179f37ab7b8d32401a2ea11be5c'),
    'exe-dvacore-15004': ('dvacore', 0x15004, 0x15240,
        'd47d510b50ac4a18b8758a2bf3c9fd5cc3af1809f71e79c89d3efb9d13b97d3b'),
    'exe-dvacore-15450': ('dvacore', 0x15450, 0x15b64,
        'aa3f72d00e39a896b065d43d5e316afa97bdc7b720fa778d4ba1a97354eaadba'),
    'exe-dvacore-15b64': ('dvacore', 0x15b64, 0x15c70,
        'b55f69b352b7a8a762e5c4c9a5960508356fa4638573a6aa5b6c98ae9fc43515'),
    'exe-dvacore-15c70': ('dvacore', 0x15c70, 0x15d7c,
        '28c6a77838c7f081d11df9a897e3bea165682a3b25336725dd8e26b2db25d0e8'),
    'exe-dvacore-15d7c': ('dvacore', 0x15d7c, 0x15ea4,
        '89831e1fa919b2ae6224559f8bfdd1ccceee9a98ec53eba8501b4ab8227599b7'),
    'exe-dvacore-17bb0': ('dvacore', 0x17bb0, 0x17dd4,
        'ec8c2cdc4d79dbcc70ecec843cdfc6614fcdc6584eecb0ce7c34981014017644'),
    'exe-dvacore-18644': ('dvacore', 0x18644, 0x1864c,
        'b914dcd2aed3ef22b3f9c5f231e25ea5dd593500c262bf3018d37228b705c9ac'),
    'exe-dvacore-243bbc': ('dvacore', 0x243bbc, 0x243c24,
        '43bc3516a40e205f47001c025fc0aa7b85265e52c4d1331408ad7fb5c7e22cc5'),
    'exe-dvacore-243c24': ('dvacore', 0x243c24, 0x243c38,
        '8fdf29f7bf2a740373f5d8ddc01e3bec14de2d9306bf8a99daac48c6895b0da6'),
}

TABLE_START = 0x39ded0
TABLE_TARGETS = (0, 0x39df80, 0x14c30, 0x14d8c, 0x14da0, 0x14ff4,
                 0x15004, 0x15240, 0x15328, 0x15330, 0x1537c, 0x15450,
                 0x15b64, 0x15c70, 0x15d7c)

def collect_symbols(raw, image, parser):
    require(image in IDENTITIES, 'unreviewed executor image')
    uuid, symbols, strings, text = IDENTITIES[image]
    bodies = [row for row in BODIES if row[0] == image]
    requested = {r[3]: (r[1], r[2]) for r in bodies}
    partitions = {r[3]: tuple((w[1], w[2]) for w in WINDOWS.values()
                             if w[0] == image and r[1] <= w[1] < r[2])
                  for r in bodies}
    result = parser(raw, uuid, requested, partitions=partitions)
    require((result['nlist_symbols'], result['string_bytes'], result['text_symbols']) ==
            (symbols, strings, text), 'original executor inventory drift')
    for _, start, end, name, digest in bodies:
        require(result['selected'][name]['body_sha256'] == digest,
                'complete executor body bytes differ')
    return result


def verify_window(text, label, verify):
    require(label in WINDOWS, 'unreviewed executor window')
    _, start, end, expected = WINDOWS[label]
    count = verify(text, start, end, expected)
    return {'decoded_instructions': count, 'all_instruction_digest': expected,
            'claim': 'file-only-executor-not-host-admission-or-drain'}


def verify_table(words, fixups, chains):
    formats = re.findall(r'pointer_format:\s+(\d+)\s+\(([^)]+)\)', chains)
    require(formats and all(pair == ('6', 'DYLD_CHAINED_PTR_64_OFFSET') for pair in formats),
            'executor table fixup format differs')
    require(len(words) == len(TABLE_TARGETS) and words[0] == 0,
            'executor table coverage/header differs')
    require(all(isinstance(w, int) and 0 <= w < 1 << 64 and
                not w & ((1 << 63) | (0x7fff << 36)) for w in words[1:]),
            'executor table is bound, high-address or reserved')
    targets = (0,) + tuple(w & ((1 << 36)-1) for w in words[1:])
    require(targets == TABLE_TARGETS, 'executor table targets differ')
    rows = []
    for address, kind, target in re.findall(
            r'^\s*__DATA_CONST\s+__const\s+0x([0-9a-fA-F]+)\s+(\S+)\s+([^\n]+)',
            fixups, re.M):
        address = int(address, 16)
        if TABLE_START <= address < TABLE_START + len(TABLE_TARGETS)*8:
            require(kind == 'rebase' and re.fullmatch(r'0x[0-9a-fA-F]+', target.strip()),
                    'executor table fixup is not a plain rebase')
            rows.append((address, int(target.strip(), 16)))
    require(rows == [(TABLE_START+i*8, target) for i, target in enumerate(TABLE_TARGETS) if i],
            'executor table fixups differ or are incomplete/duplicated')
    return {'rebases': len(TABLE_TARGETS)-1,
            'slot_targets': {hex((i-2)*8): hex(target) for i, target in enumerate(TABLE_TARGETS) if i >= 2},
            'claim': 'file-executor-table-not-live-ABI-or-host-barrier'}
