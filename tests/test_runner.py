import importlib.util
import io
import json
from pathlib import Path
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('runner', ROOT / 'v2/run.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
EXAMPLES = json.loads((ROOT / 'v2/examples.json').read_text())


class RunnerTests(unittest.TestCase):
    def test_every_request_matches_the_catalog(self):
        env = {'LINKT_API_KEY': 'fixture-key', 'CAMPAIGN_ID': '0190a4e2-0000-7000-8000-000000000010', 'ACCOUNT_ID': '0190a4e2-0000-7000-8000-000000000020'}
        for example in EXAMPLES:
            with self.subTest(example=example['id']):
                request = runner.prepare(example, env, allow_write=True)
                self.assertEqual(request.method, example['method'])
                self.assertTrue(request.full_url.startswith('https://api.linkt.ai/v2/'))
                self.assertNotIn('{', request.full_url)
                self.assertEqual(request.get_header('X-api-key'), 'fixture-key')
                if example.get('readOnly'):
                    self.assertTrue(request.full_url.endswith('?limit=5'))
                    self.assertIsNone(request.data)
                else:
                    expected = example['body'].copy()
                    if example['id'] == 'add-account':
                        expected['ids'] = [env['ACCOUNT_ID']]
                    self.assertEqual(json.loads(request.data), expected)
                    with self.assertRaisesRegex(ValueError, 'allow-write'):
                        runner.prepare(example, env)

    def test_environment_and_identifier_rejections(self):
        read = EXAMPLES[0]
        for env in [{}, {'LINKT_API_KEY':'x', 'LINKT_API_ENVIRONMENT':'unknown'}, {'LINKT_API_KEY':'x', 'LINKT_API_URL':'https://evil.example'}, {'LINKT_API_KEY':'x\nleak'}]:
            with self.assertRaises(ValueError):
                runner.prepare(read, env)
        request = runner.prepare(read, {'LINKT_API_KEY':'x', 'LINKT_API_ENVIRONMENT':'staging'})
        self.assertTrue(request.full_url.startswith('https://api-staging.linkt.ai/'))
        member = next(item for item in EXAMPLES if item['id'] == 'add-account')
        with self.assertRaises(ValueError):
            runner.prepare(member, {'LINKT_API_KEY':'x'}, allow_write=True)

    def test_timeout_one_request_and_size_bound(self):
        opener = MagicMock()
        opener.open.return_value.__enter__.return_value = io.BytesIO(b'{"data":[],"next_cursor":null}')
        request = runner.prepare(EXAMPLES[0], {'LINKT_API_KEY':'x'})
        self.assertEqual(runner.execute(request, opener), {'data':[], 'next_cursor':None})
        opener.open.assert_called_once_with(request, timeout=15)
        opener.open.reset_mock()
        opener.open.side_effect = TimeoutError()
        with self.assertRaises(TimeoutError):
            runner.execute(request, opener)
        opener.open.assert_called_once()
        opener.open.side_effect = None
        opener.open.return_value.__enter__.return_value = io.BytesIO(b'x' * 2_000_001)
        with self.assertRaisesRegex(ValueError, 'size limit'):
            runner.execute(request, opener)

    def test_actual_redirect_does_not_forward_credentials(self):
        received = []
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                received.append(self.path)
                self.send_response(302)
                self.send_header('Location', '/credential-target')
                self.end_headers()
            def log_message(self, *args):
                pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            request = Request(f'http://127.0.0.1:{server.server_port}/redirect', headers={'x-api-key':'fixture'})
            with self.assertRaisesRegex(ValueError, 'HTTP 302'):
                runner.execute(request)
            self.assertEqual(received, ['/redirect'])
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == '__main__':
    unittest.main()
