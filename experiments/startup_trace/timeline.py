"""Bounded timing evidence. Never authorizes, retries, or changes a deadline."""
import ctypes
import sys
import time

FIELDS = ('wall_ms', 'monotonic_ms', 'absolute_ticks', 'continuous_ticks',
          'timebase_numer', 'timebase_denom')
LEAVES = ('request-received', 'request-parsed', 'request-deadline-check',
          'request-binding-before', 'request-binding-after')


def snapshot():
    wall = time.time_ns() // 1000000
    monotonic = time.monotonic_ns() // 1000000
    if sys.platform != 'darwin':
        return dict(zip(FIELDS, (wall, monotonic, None, None, None, None)))
    class Scale(ctypes.Structure):
        _fields_ = [('numer', ctypes.c_uint32), ('denom', ctypes.c_uint32)]
    lib = ctypes.CDLL('/usr/lib/libSystem.B.dylib')
    lib.mach_absolute_time.argtypes = []; lib.mach_absolute_time.restype = ctypes.c_uint64
    lib.mach_continuous_time.argtypes = []; lib.mach_continuous_time.restype = ctypes.c_uint64
    lib.mach_timebase_info.argtypes = [ctypes.POINTER(Scale)]; lib.mach_timebase_info.restype = ctypes.c_int
    scale = Scale()
    if lib.mach_timebase_info(ctypes.byref(scale)) != 0 or not scale.numer or not scale.denom:
        raise ValueError('clock scale unavailable')
    return dict(zip(FIELDS, (wall, monotonic, lib.mach_absolute_time(), lib.mach_continuous_time(), scale.numer, scale.denom)))


def validate(sample):
    if not isinstance(sample, dict) or set(sample) != set(FIELDS):
        raise ValueError('timing schema differs')
    for name, value in sample.items():
        if type(value) is not int or not 0 <= value < 2**64:
            raise ValueError('timing number differs')
    if not 0 < sample['timebase_numer'] < 2**32 or not 0 < sample['timebase_denom'] < 2**32:
        raise ValueError('timing scale differs')
    return sample


def compare(published, received, deadline):
    a, b = validate(published), validate(received)
    if type(deadline) is not int or not 0 <= deadline < 2**64:
        raise ValueError('timing deadline differs')
    if (a['timebase_numer'], a['timebase_denom']) != (b['timebase_numer'], b['timebase_denom']):
        raise ValueError('clock domains differ')
    def elapsed(name):
        ticks = b[name] - a[name]
        if ticks < 0: raise ValueError('elapsed clock went backwards')
        return ticks * a['timebase_numer'] // (a['timebase_denom'] * 1000000)
    active, continuous = elapsed('absolute_ticks'), elapsed('continuous_ticks')
    wall = b['wall_ms'] - a['wall_ms']
    suspension, shift = continuous - active, wall - continuous
    if suspension < -1000: raise ValueError('clock samples inconsistent')
    seconds = b['wall_ms'] // 1000
    window = 'EXPIRED' if deadline <= seconds else 'FUTURE_OUTSIDE_BUDGET' if deadline-seconds > 120 else 'WITHIN_BUDGET'
    return {'wall_elapsed_ms':wall, 'active_elapsed_ms':active, 'continuous_elapsed_ms':continuous,
            'suspension_excess_ms':suspension, 'wall_vs_continuous_ms':shift,
            'suspension_observed':suspension > 1000, 'wall_shift_observed':abs(shift) > 1000,
            'deadline_window':window, 'scope':'timing evidence only; no authorization or causal exclusivity'}


def parse_native(raw, build, pid, birth, phase):
    if len(raw) > 2048: raise ValueError('timing receipt too large')
    lines = raw.decode('ascii').splitlines()
    if not lines or lines[0] != 'AEHL-CAL-TIMING-1': raise ValueError('timing magic differs')
    fields = {}
    for line in lines[1:]:
        name, sep, value = line.partition('=')
        if not sep or name in fields: raise ValueError('timing field differs')
        fields[name] = value
    if set(fields) != set(FIELDS) | {'build','pid','birth','phase','deadline'}:
        raise ValueError('timing fields differ')
    if fields['build'] != build: raise ValueError('timing build differs')
    numbers = {}
    for name in set(fields)-{'build'}:
        value=fields[name]
        if not value.isascii() or not value.isdecimal() or len(value)>20:
            raise ValueError('timing integer differs')
        numbers[name]=int(value)
        if numbers[name]>=2**64: raise ValueError('timing integer range differs')
    if (numbers['pid'],numbers['birth'],numbers['phase']) != (pid,birth,phase):
        raise ValueError('timing identity differs')
    sample=validate({name:numbers[name] for name in FIELDS})
    return {'sample':sample,'deadline':numbers['deadline'],'phase':phase}
