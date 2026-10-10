"""Stop-scoped bounded bytes; mapping is necessary, not an ownership proof.

Only the fixture collector supplies a reviewed immutable backing extent. Adobe
objects are not admitted. Returned bytes are copies; no borrowed object escapes.
"""
from experiments.resource_trace.core import need, uint

MAX_READ = 4096


def extent(address, size, base, length):
    need(all(uint(x, True) for x in (address, size, base, length)), 'invalid borrowed extent')
    need(size <= MAX_READ and length <= MAX_READ, 'borrow byte budget')
    need(base + length < 2**64 and address + size < 2**64, 'borrow extent overflow')
    need(base <= address and address + size <= base + length, 'read outside backing extent')


def read(process, api, identity, stop_id, address, size, base, length):
    """Identity must freshly verify PID/birth/executable before and after access."""
    extent(address, size, base, length)

    def stable():
        identity()
        need(process.GetState() == api.eStateStopped and process.GetStopID() == stop_id,
             'borrow stop changed')

    stable()
    region = api.SBMemoryRegionInfo()
    need(process.GetMemoryRegionInfo(address, region).Success(), 'mapping query failed')
    need(region.IsMapped() and region.IsReadable() and not region.IsExecutable() and
         region.GetRegionBase() <= base and base + length <= region.GetRegionEnd(),
         'borrow mapping/permissions/extent differs')
    mapping = (region.GetRegionBase(), region.GetRegionEnd())
    stable()
    error = api.SBError()
    raw = process.ReadMemory(address, size, error)
    need(error.Success() and type(raw) is bytes and len(raw) == size, 'borrow failed or short read')
    stable()
    after = api.SBMemoryRegionInfo()
    need(process.GetMemoryRegionInfo(address, after).Success() and after.IsMapped() and
         after.IsReadable() and not after.IsExecutable() and
         (after.GetRegionBase(), after.GetRegionEnd()) == mapping, 'mapping changed during read')
    stable()
    return raw, {'stop_id': stop_id, 'address': address, 'size': size,
                 'backing_base': base, 'backing_length': length,
                 'mapping_base': mapping[0], 'mapping_end': mapping[1],
                 'lifetime': 'OWNED_FIXTURE_CALL_SCOPE_ONLY'}
