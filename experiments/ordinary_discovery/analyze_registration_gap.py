"""Read-only analysis of saved scoped-loader evidence, never an AE operation.

The interpretation model is InternalLoader.cpp blob df64e125a984199e45cd777eef8c16a556ec393b.
Hash verification establishes supplied file identity, not acquisition provenance.
An analysis PASS is not a live-registration PASS. Output contains no file paths,
raw pointers, registry inventory, request tokens or host calls.
"""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
from urllib.parse import quote, unquote

MODEL_BLOB = 'df64e125a984199e45cd777eef8c16a556ec393b'
LIMIT = 8 * 1024 * 1024
PTR = r'(?:0x[0-9a-fA-F]{1,16}|\(nil\)|0)'


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def read_verified(path, expected_hash, limit=LIMIT):
    require(re.fullmatch(r'[0-9a-f]{64}', expected_hash), 'invalid expected hash')
    path = Path(path).absolute()
    require(not any(p.is_symlink() for p in (path, *path.parents)), 'symlink rejected')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        before = os.fstat(fd)
        require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
                0 < before.st_size <= limit, 'invalid evidence file')
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            data = stream.read(limit + 1)
        after = os.fstat(fd)
        fields = ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns', 'st_ctime_ns', 'st_nlink')
        require(len(data) == before.st_size and all(getattr(before, k) == getattr(after, k)
                for k in fields), 'evidence changed during read')
        require(hashlib.sha256(data).hexdigest() == expected_hash, 'evidence hash mismatch')
        return data
    finally:
        os.close(fd)


def snapshot(raw):
    text = raw.decode('utf-8', errors='strict')
    require(text.endswith('\n') and '\r' not in text, 'incomplete snapshot')
    lines = text[:-1].split('\n')
    require(len(lines) >= 3 and lines[0] == 'AEHL-SNAPSHOT-1', 'invalid snapshot header')
    require(re.fullmatch(r'[1-9][0-9]{0,15}', lines[1]), 'invalid project revision')
    names = lines[2:]
    require(0 < len(names) <= 10000 and names == sorted(names), 'invalid registry ordering/count')
    for name in names:
        decoded = unquote(name, encoding='utf-8', errors='strict')
        require(name and all(ord(c) >= 32 and ord(c) != 127 for c in decoded) and
                quote(decoded, safe="~()*!.'-_") == name, 'invalid encoded match name')
    return lines[1], Counter(names)


def one(pattern, lines):
    matches = [m for line in lines if (m := re.fullmatch(pattern, line))]
    require(len(matches) == 1, 'missing or ambiguous loader record')
    return matches[0]


def saved_path(value):
    require(value and len(value) <= 4096 and all(ord(c) >= 32 and ord(c) != 127 for c in value),
            'invalid saved path')
    path = PurePosixPath(value)
    require(path.is_absolute() and str(path) == value and '..' not in path.parts and value != '/',
            'noncanonical saved path')
    return value


def analyze(log, before_raw, after_raw, scan_root, fixture_image, fixture_match):
    root, image = saved_path(scan_root), saved_path(fixture_image)
    require(image.startswith(root + '/'), 'fixture outside scan root')
    require(fixture_match and len(fixture_match) <= 1024 and
            all(ord(c) >= 32 and ord(c) != 127 for c in fixture_match), 'invalid fixture match name')
    target = quote(fixture_match, safe="~()*!.'-_")
    lines = log.decode('utf-8', errors='strict').splitlines()
    call = r'internal-loader: calling ML::LoadPlugins root=(.+) fn=' + PTR
    calls = [(i, m.group(1)) for i, line in enumerate(lines) if (m := re.fullmatch(call, line))]
    starts = [i for i, value in calls if value == root]
    require(len(starts) == 1, 'missing or replayed scoped transaction')
    start = starts[0]
    stop = next((i for i, _ in calls if i > start), len(lines))
    section = lines[start:stop]
    returned = one(r'internal-loader: returned=([0-9]{1,10}) output=\[(' + PTR +
                   '),(' + PTR + '),(' + PTR + r')\]', section)
    loaded = int(returned[1])
    pointers = [0 if value in ('(nil)', '0') else int(value, 16) for value in returned.groups()[1:]]
    begin, end, capacity = pointers
    require(0 <= loaded <= 2147483647 and begin <= end <= capacity and
            (begin != 0 or end == capacity == 0), 'invalid loader return/vector')
    modules = one(r'internal-loader: video modules before=([0-9]{1,5}) after=([0-9]{1,5}) added=([0-9]{1,5})', section)
    old, new, added = map(int, modules.groups())
    require(max(old, new, added) <= 10000 and added <= new <= old + added,
            'inconsistent module counts')
    complete = one(r'internal-loader: ordinary registration complete loaded=([0-9]{1,10}) added_modules=([0-9]{1,5})', section)
    require((loaded, added) == tuple(map(int, complete.groups())), 'inconsistent completion record')
    notifications = [line for line in section if line.startswith('internal-loader: FLT_NotifyFilterLoadingDone')]
    require(not notifications if added == 0 else notifications == [
        'internal-loader: FLT_NotifyFilterLoadingDone returned added=' + str(added)],
        'inconsistent notifier record')
    dyld = one(r'internal-loader: dyld image=' + re.escape(image) +
               r' PluginDataEntryFunction2=(' + PTR + r') EffectMain=(' + PTR + ')', section)
    images = [line for line in section if line.startswith('internal-loader: dyld image=' + root + '/')]
    require(len(images) == 1, 'expected one scoped fixture image')
    one(r'internal-loader: dyld root=' + re.escape(root) + r' matched_images=1', section)
    # Validate ordering too: concatenated/out-of-order fragments are not a transaction.
    ordered = [section.index(returned[0]), section.index(dyld[0]), section.index(modules[0])]
    if notifications:
        ordered.append(section.index(notifications[0]))
    ordered.append(section.index(complete[0]))
    require(ordered == sorted(ordered), 'out-of-order loader records')
    before_revision, before = snapshot(before_raw)
    after_revision, after = snapshot(after_raw)
    same_revision = before_revision == after_revision
    exact_addition = not before[target] and after == before + Counter({target: 1})
    missing = after[target] == 0
    return {
        'analysis_status': 'PASS', 'scope': 'saved-evidence-only-not-live-AE-proof',
        'interpretation_source_blob': MODEL_BLOB,
        'loader_return': loaded, 'returned_vector_bytes': end - begin,
        'returned_vector_element_type': 'UNOBSERVED',
        'fixture_image_observed': True,
        'dynamic_export_address_observed': dyld[1] not in ('0', '(nil)') and int(dyld[1], 16) != 0,
        'video_modules': {'before_count': old, 'after_count': new, 'added_count': added},
        'notifier_dispatch_inference': 'SKIPPED_ZERO_NEW_MODULES' if not added else 'RETURN_LOGGED',
        'registry': {'before_count': sum(before.values()), 'after_count': sum(after.values()),
                     'identities_unchanged': before == after, 'target_absent_after': missing,
                     'revision_unchanged': same_revision,
                     'exact_addition_check': 'PASS' if same_revision and exact_addition else 'FAIL'},
        'next_boundary': 'PiPL interpretation / video-module creation and publication' if missing and not added
                         else 'Not localized by these records',
        'parsed_pipl_evidence': 'BLOCKED', 'current_host_state': 'BLOCKED',
        'live_registration_gate': 'NOT RUN', 'apply_render': 'NOT RUN',
        'limits': ['Hashes identify supplied bytes, not their acquisition or runtime source.',
                   'Image presence is not proof of newly loading it or executing its entrypoint.',
                   'Counts do not prove video-module identity equality.',
                   'No PiPL contents, runtime receiver, PID/start correlation or current AE state is observed.',
                   'A vector byte span is not a plugin count or a callable ABI.'],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('loader-log', 'before', 'after'):
        parser.add_argument('--' + name, type=Path, required=True)
        parser.add_argument('--' + name + '-sha256', required=True)
    parser.add_argument('--scan-root', required=True)
    parser.add_argument('--fixture-image', required=True)
    parser.add_argument('--fixture-match', required=True)
    args = parser.parse_args(argv)
    try:
        data = {name: read_verified(getattr(args, name), getattr(args, name + '_sha256'))
                for name in ('loader_log', 'before', 'after')}
        report = analyze(data['loader_log'], data['before'], data['after'],
                         args.scan_root, args.fixture_image, args.fixture_match)
        report['input_sha256'] = {name: hashlib.sha256(raw).hexdigest() for name, raw in data.items()}
        code = 0
    except (ValueError, UnicodeError, OSError):
        # Do not leak supplied paths, content, addresses or registry names on errors.
        report = {'analysis_status': 'BLOCKED', 'scope': 'saved-evidence-only-not-live-AE-proof',
                  'reason': 'Evidence unavailable, changed, unverified, malformed or ambiguous.'}
        code = 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
