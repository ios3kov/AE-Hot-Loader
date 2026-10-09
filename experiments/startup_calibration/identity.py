"""Own diagnostic naming; not an SDK-wide match-name length contract."""


def marker_match(run_id):
    if not isinstance(run_id, str) or len(run_id) != 32 or set(run_id) - set('0123456789abcdef'):
        raise ValueError('run ID must be32 lowercase hex characters')
    # The exact target host returned only31 bytes of our previous44-byte match.
    # Preserve96 bits here; the complete nonce and source remain in the BuildID.
    return 'AEHL.M.' + run_id[:24]


def resource_match(run_id, discriminate=False):
    """A separate resource identity only for the read-only route experiment."""
    match = marker_match(run_id)
    if type(discriminate) is not bool:
        raise ValueError('route discriminator must be Boolean')
    return 'AEHL.R.' + run_id[:24] if discriminate else match
