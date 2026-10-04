"""Own diagnostic naming; not an SDK-wide match-name length contract."""


def marker_match(run_id):
    if not isinstance(run_id, str) or len(run_id) != 32 or set(run_id) - set('0123456789abcdef'):
        raise ValueError('run ID must be32 lowercase hex characters')
    # The exact target host returned only31 bytes of our previous44-byte match.
    # Preserve96 bits here; the complete nonce and source remain in the BuildID.
    return 'AEHL.M.' + run_id[:24]
