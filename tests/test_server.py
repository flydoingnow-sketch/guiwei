import importlib.util
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
import urllib.request
import urllib.error
from http.server import ThreadingHTTPServer

class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        os.environ['GUIWEI_DATA_DIR'] = cls.tmp.name
        spec = importlib.util.spec_from_file_location('guiwei_server', Path(__file__).resolve().parents[1] / 'server.py')
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), cls.module.Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}'
        cls.client = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        cls.tmp.cleanup()
        os.environ.pop('GUIWEI_DATA_DIR', None)

    def post(self, tasks, origin='http://127.0.0.1:18743'):
        request = urllib.request.Request(self.base + '/api/tasks', data=json.dumps(tasks).encode(), headers={'Content-Type': 'application/json', 'Origin': origin})
        try:
            with self.client.open(request) as response:
                return response.status
        except urllib.error.HTTPError as error:
            return error.code

    def test_deadline_roundtrip(self):
        tasks = [{'id': 'test', 'text': '示例任务', 'q': 'plan', 'done': False, 'deadline': '2026-10-14T10:00'}]
        self.assertEqual(self.post(tasks), 200)
        self.assertEqual(json.loads(self.module.DATA.read_text()), tasks)

    def test_invalid_tasks_do_not_overwrite_data(self):
        self.post([])
        self.assertEqual(self.post([{'text': 'x', 'q': 'invalid'}]), 400)
        self.assertEqual(json.loads(self.module.DATA.read_text()), [])

    def test_external_origin_rejected(self):
        self.assertEqual(self.post([], 'https://example.com'), 403)

    def test_page_available(self):
        with self.client.open(self.base + '/') as response:
            self.assertIn('归位', response.read().decode())

if __name__ == '__main__':
    unittest.main()
