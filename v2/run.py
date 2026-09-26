"""Run one bounded V2 HTTP example without a client SDK."""
from __future__ import annotations

import argparse
import copy
import json
import os
from pathlib import Path
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
from uuid import UUID

ROOT = Path(__file__).resolve().parents[1]


def load_environment():
    """Load root .env without overriding the calling environment or running shell code."""
    source = ROOT / '.env'
    if source.exists():
        for line in source.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            key, separator, value = line.partition('=')
            if not separator or not re.fullmatch(r'[A-Z_][A-Z0-9_]*', key.strip()):
                raise ValueError('Invalid .env assignment')
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in '\"\'':
                value = value[1:-1]
            os.environ.setdefault(key.strip(), value)


def prepare(example, environment, *, allow_write=False):
    """Validate the destination and identifiers before attaching credentials."""
    origins = {'production': 'https://api.linkt.ai', 'staging': 'https://api-staging.linkt.ai'}
    selected = environment.get('LINKT_API_ENVIRONMENT', 'production')
    if selected not in origins:
        raise ValueError('LINKT_API_ENVIRONMENT must be production or staging')
    origin = environment.get('LINKT_API_URL', origins[selected])
    if origin != origins[selected]:
        raise ValueError('LINKT_API_URL does not match the selected environment')
    key = environment.get('LINKT_API_KEY', '')
    if not key or any(c in key for c in '\r\n'):
        raise ValueError('Set LINKT_API_KEY for the selected environment')
    if not example.get('readOnly') and not allow_write:
        raise ValueError('This example changes data; pass --allow-write to run it')
    path = example['path']
    for name in example.get('pathParameters', {}):
        value = environment.get(name.upper(), '')
        try:
            UUID(value)
        except ValueError:
            raise ValueError(f'Set {name.upper()} to a real UUID') from None
        path = path.replace('{' + name + '}', value)
    if not path.startswith('/') or '{' in path or urlsplit(path).netloc:
        raise ValueError('Invalid example path')
    body = copy.deepcopy(example.get('body'))
    if example['id'] == 'add-account':
        account = environment.get('ACCOUNT_ID', '')
        try:
            UUID(account)
        except ValueError:
            raise ValueError('Set ACCOUNT_ID to a real UUID') from None
        body['ids'] = [account]
    query = urlencode(example.get('query', {}))
    url = origin + '/v2' + path + ('?' + query if query else '')
    headers = {'x-api-key': key, 'Accept': 'application/json'}
    data = None
    if body is not None:
        headers['Content-Type'] = 'application/json'
        data = json.dumps(body).encode()
    return Request(url, data=data, headers=headers, method=example['method'])


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Never forward an API key through an unexpected redirect.
        return None


def execute(request, opener=None):
    """Send one request with a timeout and no automatic mutation retry."""
    opener = opener or build_opener(NoRedirect())
    try:
        with opener.open(request, timeout=15) as response:
            payload = response.read(2_000_001)
            if len(payload) > 2_000_000:
                raise ValueError('Response exceeds the example size limit')
            return json.loads(payload)
    except HTTPError as error:
        error.close()
        raise ValueError(f'HTTP {error.code}; check the key, environment and resource permissions') from None
    except URLError:
        raise ValueError('Request failed; check connectivity before retrying') from None


def main():
    examples = json.loads((ROOT / 'v2/examples.json').read_text())
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('example', choices=[item['id'] for item in examples])
    parser.add_argument('--allow-write', action='store_true')
    args = parser.parse_args()
    try:
        load_environment()
        example = next(item for item in examples if item['id'] == args.example)
        print(json.dumps(execute(prepare(example, os.environ, allow_write=args.allow_write)), indent=2))
    except (ValueError, TimeoutError):
        # Do not print arbitrary response bodies or exception URLs containing user data.
        parser.exit(1, 'Example failed. Check configuration, permissions and the selected resource.\n')


if __name__ == '__main__':
    main()
