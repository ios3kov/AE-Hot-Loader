"""Fixed original U suspend-context evidence, never a callable Adobe ABI."""

UUID = '3053ea7ea176315d900b9f17cc96dbe5'
INVENTORY = (14740, 308320, 2497)

# Exact original names/next-defined-text ends and complete-byte digests.
BODIES = (
    ('U', 0x153c4, 0x15a80,
     '__ZN16U_SuspendContextC2Ev',
     '0c993d9f887ec365a5ffac55f67f7162532246ef68a4dbc10b0bc7775a8841c1'),
    ('U', 0x15c24, 0x16048,
     '__ZN16U_SuspendContextD2Ev',
     '66a6173116bf2b1786a3765ab9a49ebd98c13ca7332970be1a8ad9e48a8cd7fc'),
    ('U', 0x16960, 0x169a8,
     '__ZN16U_SuspendContext17NewSuspendContextEv',
     'b5e5b4bb69adbd09fcddafccaabc0a7be0e2c85a7b693e5c50f417a5f17a55a4'),
    ('U', 0x164e0, 0x164e4,
     '__ZN16U_SuspendContext22CallOnThreadedExecutorERKNSt3__110shared_ptrIN7dvacore7threads21AsyncThreadedExecutorEEERKNS0_8functionIFivEEE',
     '788f1512f26f87f558ccda89030f23036527961be061f31e047ad5b93b8aafe2'),
    ('U', 0x164e4, 0x16960,
     '__ZN16U_SuspendContext14CallOnExecutorINSt3__110shared_ptrIN7dvacore7threads21AsyncThreadedExecutorEEEEEiRKT_RKNS1_8functionIFivEEE',
     'c970d099b99775a31f501a54794055462ceaed132ada81a9d28db5f92d547dc3'),
    ('U', 0x16060, 0x16064,
     '__ZN16U_SuspendContext30CallOnEventLoopAdaptorExecutorERKNSt3__110shared_ptrIN7dvacore7threads21AsyncEventLoopAdaptorEEERKNS0_8functionIFivEEE',
     '788f1512f26f87f558ccda89030f23036527961be061f31e047ad5b93b8aafe2'),
    ('U', 0x16064, 0x164e0,
     '__ZN16U_SuspendContext14CallOnExecutorINSt3__110shared_ptrIN7dvacore7threads21AsyncEventLoopAdaptorEEEEEiRKT_RKNS1_8functionIFivEEE',
     '68c9096ec7329c627b2ded43d082a652c0ccf7cea9377f8a7812a54d54b3daa4'),
    ('U', 0x16a80, 0x16e4c,
     '__ZN16U_SuspendContext13ExecuteStaticERKNSt3__18functionIFivEEERKNS0_10shared_ptrIN7dvacore7threads12OpenOnceGateEEERKN5boost10shared_ptrI9U_ContextEERKNSE_IKSF_EERKNSE_I15U_RenderContextEERKNS6_I22Up_PerThreadErrorStateEERNSE_IiEE',
     'f74222b0ef2b6337d5fb431c6871b3c2a33452246c7907b49028e48fd082393c'),
    ('U', 0x16e54, 0x16e6c,
     '__ZN16U_SuspendContext36TerminateAndFailAllSuspendedContextsEv',
     '8f9d7a21951e0ba1da7eb77f81e2e6cd1806574c2b43d132513d777f6302070f'),
    ('U', 0x16e6c, 0x16fe4,
     '__ZN16U_SuspendContext15U_ResumeContextC2ERKN5boost10shared_ptrI9U_ContextEERKNS2_IKS3_EERKNS2_I15U_RenderContextEE',
     '258660c3c4ff164118ebaeb4b5641aeb74feb356415b3ae5828406e547ea0d59'),
    ('U', 0x16fe4, 0x171f0,
     '__ZN16U_SuspendContext15U_ResumeContextD2Ev',
     'd1c6d3286470fc71a87a8633b673ccea67534abd3fac78ecbfeae75945c62959'),
    ('U', 0x131bc, 0x131d8,
     '__ZN16U_SuspendContext16GetRenderContextEv',
     '68329af0cdd14edc50aa3d87aae320bac7e6f1f16a1f7db71abad2596e45a68b'),
    ('U', 0x1286c, 0x12ca0,
     '__ZL24DetachNonConstContextTLSPKcx',
     '7ec622538d2e0125ba08b8d58ac7225a0329b0bfac626a2aa548ddb8cec26c1b'),
    ('U', 0x13ae8, 0x13e24,
     '__ZL24AttachNonConstContextTLSRKN5boost10shared_ptrI9U_ContextEE',
     '6a8bf9506cecf949680839a417a6645c47d740826097f13f10a67693d8e36d09'),
    ('U', 0x140f0, 0x14418,
     '__ZL21AttachConstContextTLSRKN5boost10shared_ptrIK9U_ContextEE',
     '8b130d398babd25efa77bd28a81a60b052ce3b5cf56128f4d4436d200bd9c796'),
    ('U', 0x148e0, 0x14cd8,
     '__ZL21DetachConstContextTLSPKcx',
     '9bd3b25815526fdfe7a57f04aee6a524f5ea81f5e09ead3ca680c1cc02204295'),
    ('U', 0x29538, 0x29874,
     '__Z25Up_AttachRenderContextTLSRKN5boost10shared_ptrI15U_RenderContextEE',
     'd275891193f702aa2949ea505c64dfa91c810f581345d31331c12d9bc4d0eb17'),
    ('U', 0x29104, 0x29538,
     '__Z25Up_DetachRenderContextTLSPKcx',
     'ce716564a78875a7d7c170255ebea6981f719c5be6e17327ddc4e4cd1233cb22'),
    ('U', 0x131d8, 0x13348,
     '__ZN9U_Context10GetCurrentEb',
     'a3619124274f7713f8a105dd703059c22a481f37f2c4b681a154c7923eca38f3'),
    ('U', 0x13528, 0x13680,
     '__ZN9U_Context10HasCurrentEb',
     '8d7197020b316da64e127ddc6c6d7df385ac1a8db23af54e1c50e39125e66484'),
    ('U', 0x2a5e0, 0x2a77c,
     '__ZN15U_RenderContext10GetCurrentEb',
     'b5ac547f08cc99c25189a76a95ec6b6c392db18dc76eace98ddb4dc709efcd18'),
    ('U', 0x1a300, 0x1a35c,
     '__ZNSt3__120__shared_ptr_pointerIPN9U_Context15ActivationTokenENS_10shared_ptrIS2_E27__shared_ptr_default_deleteIS2_S2_EENS_9allocatorIS2_EEE16__on_zero_sharedEv',
     'db26dd43477f8fef428f02ced7776d9ea5edaa5e2592f64c178cdf49457376e4'),
    ('U', 0x2bb80, 0x2bbdc,
     '__ZNSt3__120__shared_ptr_pointerIPN15U_RenderContext15ActivationTokenENS_10shared_ptrIS2_E27__shared_ptr_default_deleteIS2_S2_EENS_9allocatorIS2_EEE16__on_zero_sharedEv',
     '38e09a978fcfef25e7c52281af2729dbbdb6eeaba761fe4a0a4bf857d3c385b4'),
    ('U', 0x29874, 0x29a54,
     '__ZN15U_RenderContext18GetActivationTokenEb',
     '04275abffae042be5952fffb0c90a7363c5410a3f38b5718d485be5cb673c097'),
    ('U', 0x2af4c, 0x2afa0,
     '__ZN15U_RenderContext20ClearActivationTokenEv',
     'ab5f39cb5762402ea0837e3a8ff2e0a5fb069f1ac71503889d8b9753c902bec0'),
    ('U', 0x14cd8, 0x14eb8,
     '__ZN9U_Context18GetActivationTokenEb',
     '8db63a708ddbfecc091954783ce745de0d8afaaeb9f90d21e5ae2e86177a8ffd'),
    ('U', 0x146e0, 0x14734,
     '__ZN9U_Context20ClearActivationTokenEv',
     '835e7cbee80ff3052787b18ccbc9ddae2a7bc583f531cbbcfdd85ea723805f64'),
)

# Each entire body fits the unchanged4096-byte capture limit.
WINDOWS = {
    'sus-U-153c4': ('U', 0x153c4, 0x15a80,
        '207f8143389259821a0b3afe5dd9d11c4571e461023b65a5062b19a95828a049'),
    'sus-U-15c24': ('U', 0x15c24, 0x16048,
        '5b78b1b9988ba34c4c39aa8fc7e06c58f9b719b2976e2429aa610578b70e4615'),
    'sus-U-16960': ('U', 0x16960, 0x169a8,
        'd4bda9e38117fd94befcd4483fd81a0ada56d166e056cb24ce3ba4e8750e80b9'),
    'sus-U-164e0': ('U', 0x164e0, 0x164e4,
        '17df5af1f826b1885bc2ff9493337d458ae50c8db04ac78403c6e0a257488e6c'),
    'sus-U-164e4': ('U', 0x164e4, 0x16960,
        'f758bf61d372d555914940f5197145c30d86da2e83521f775d732f7ddd7d9184'),
    'sus-U-16060': ('U', 0x16060, 0x16064,
        '88b682a8376c3792a24a06703b31232dbdcb3342da4fa65076525c5684b25bf9'),
    'sus-U-16064': ('U', 0x16064, 0x164e0,
        '813c694275c081444deb4639b3f63160537547d64d36d738702f790e9b03deb2'),
    'sus-U-16a80': ('U', 0x16a80, 0x16e4c,
        '393bd08125fdeb5e635d99af97b976f404a195ead6f64fc4fdd69056f1996504'),
    'sus-U-16e54': ('U', 0x16e54, 0x16e6c,
        '7061878cd575d6dab4ddfbfa8ef682df6d22b1656fe6615224f9aec09d1963f6'),
    'sus-U-16e6c': ('U', 0x16e6c, 0x16fe4,
        '36144ec517d8992ea2b5dbdab79b82bfec21b8e56095df91e703270b86c9124f'),
    'sus-U-16fe4': ('U', 0x16fe4, 0x171f0,
        '5e1cbd4b418caae5764d265adc3a8e90d9a468396593aa3231103eaee0dc2d57'),
    'sus-U-131bc': ('U', 0x131bc, 0x131d8,
        '95587f6292b501e2813fdccf3841339eb6b1eafd605b09d5d564f3a81aa24f5b'),
    'sus-U-1286c': ('U', 0x1286c, 0x12ca0,
        '91361b775f22130a6f1411298e999df28268a6a5ff36c5ccb87d11c5a8664087'),
    'sus-U-13ae8': ('U', 0x13ae8, 0x13e24,
        'c1c61bf933b9b76d6cc750416ab01e73543d0a958027666088df24b100e1c290'),
    'sus-U-140f0': ('U', 0x140f0, 0x14418,
        '1cabfc34c16c21a2af0c1cffa7f87cebf55f8dbaf3f9a0df5cc3aa14a7379cc3'),
    'sus-U-148e0': ('U', 0x148e0, 0x14cd8,
        'd9b66b954803eccb4d9fa849d41a7d246fb34c4d67196fe4437db317f474f720'),
    'sus-U-29538': ('U', 0x29538, 0x29874,
        'dad3070a669e4bf48b493cea97a1b444daa11cfe5a943395bc754521a1afbdad'),
    'sus-U-29104': ('U', 0x29104, 0x29538,
        'c08e1b4797106c92dec2c0bf9b6569555574594e229a28cce516b3c214350af6'),
    'sus-U-131d8': ('U', 0x131d8, 0x13348,
        '4032da5bd9b1a06a9c5ee017ad130b8fb88e40767666ac52d1c7d3c281e8991d'),
    'sus-U-13528': ('U', 0x13528, 0x13680,
        '7e3371332a35ca94a592c6a09448790b8a7473dd7162d0f746f400f59356694c'),
    'sus-U-2a5e0': ('U', 0x2a5e0, 0x2a77c,
        '3d6bf16931e1f305a3fa654e0b726b909f267cc0ead0f3fe9163cf2faff5dafc'),
    'sus-U-1a300': ('U', 0x1a300, 0x1a35c,
        'b4ed794f8ab1e75435a708419f1fa1b7077ffba01ca05f2fd748a978c41d49ea'),
    'sus-U-2bb80': ('U', 0x2bb80, 0x2bbdc,
        '224578524df0068e068a2cbc11525d86fc2fc471e1544dbde7f16d5672c48d6e'),
    'sus-U-29874': ('U', 0x29874, 0x29a54,
        'f3516b4f6f72f545b6153e6005963bec4d75051649d41ca0961cf5fcd032acf4'),
    'sus-U-2af4c': ('U', 0x2af4c, 0x2afa0,
        '467482d8fca4e2343c892f25c62201e36692d3277efc56d25f72c6e1f9b12881'),
    'sus-U-14cd8': ('U', 0x14cd8, 0x14eb8,
        'ace1957333258e631ddb7829240bf5020973cf4244294ac55d76920505a6416d'),
    'sus-U-146e0': ('U', 0x146e0, 0x14734,
        '17f199eb3fe20b34ea41d1a7c5de8623790c7bb3b8ac26e91e77ad46da160103'),
}


def require(value, reason):
    if not value:
        raise ValueError(reason)


def collect_symbols(raw, parser):
    requested = {r[3]: (r[1], r[2]) for r in BODIES}
    result = parser(raw, UUID, requested)
    require(tuple(result.get(k) for k in ('nlist_symbols','string_bytes','text_symbols')) ==
            INVENTORY, 'original suspend-context inventory drift')
    for _, _, _, name, digest in BODIES:
        require(result.get('selected', {}).get(name, {}).get('body_sha256') == digest,
                'complete suspend-context body bytes differ')
    return result


def verify_window(text, label, verify):
    require(label in WINDOWS, 'unreviewed suspend-context window')
    _, start, end, digest = WINDOWS[label]
    count = verify(text, start, end, digest)
    return {'decoded_instructions':count,'all_instruction_digest':digest,
            'claim':'file-only-context-transfer-not-host-admission-or-drain'}


def claims():
    return {'context_scope':'CURRENT-TLS-CONTEXT-TRANSFER-NOT-GLOBAL-QUIESCENCE',
            'activation_token_scope':'PER-CONTEXT-ACTIVATION-OWNERSHIP-NOT-REGISTRY-TRANSACTION',
            'completion_scope':'ONE-DISPATCHED-CALLBACK-GATE-NOT-ALL-MFR-OR-HOUSEKEEPER',
            'terminate_scope':'PROCESS-FLAG-NOT-ALL-JOB-JOIN',
            'supported_host_owner_thread_contract':'UNKNOWN',
            'host_wide_reader_render_exclusion':'NOT PROVEN',
            'whole_effect_rollback':'NOT PROVEN',
            'native_experiment':'BLOCKED',
            'registration_apply_render':'NOT RUN'}
