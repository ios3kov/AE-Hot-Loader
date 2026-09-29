"""Compare diagnostic serialization with SDK/Rez output, without loading code."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

from build_registration_pair import pipl


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk', type=Path, required=True)
    args = parser.parse_args()
    source = Path(__file__).with_name('RegistrationControl.r')
    template = args.sdk.resolve() / 'Resources' / 'AE_General.r'
    if not template.is_file():
        parser.error('--sdk must contain Resources/AE_General.r')
    with tempfile.TemporaryDirectory(prefix='aehl-sdk-pipl-') as temp:
        resource = Path(temp) / 'control.rsrc'
        subprocess.run(['Rez', '-useDF', '-i', str(template.parent),
                        str(source), '-o', str(resource)], check=True, timeout=30)
        raw = subprocess.check_output(['DeRez', '-useDF', str(resource)],
                                      encoding='mac_roman', timeout=30)
        chunks = re.findall(r'\$"([0-9A-Fa-f ]+)"', raw)
        if not chunks:
            raise RuntimeError('DeRez returned no raw resource bytes')
        actual = bytes.fromhex(''.join(chunks))
    expected = pipl('AEHL SDK Control', 'AEHL.SDK.Control')
    result = {
        'status': 'PASS' if actual == expected else 'FAIL',
        'scope': 'SDK Rez byte equivalence only; no host acceptance claim',
        'sdk_template_sha256': hashlib.sha256(template.read_bytes()).hexdigest(),
        'control_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'sdk_payload_sha256': hashlib.sha256(actual).hexdigest(),
        'builder_payload_sha256': hashlib.sha256(expected).hexdigest(),
        'sdk_bytes': len(actual), 'builder_bytes': len(expected),
    }
    print(json.dumps(result, indent=2))
    return 0 if actual == expected else 1


if __name__ == '__main__':
    raise SystemExit(main())
