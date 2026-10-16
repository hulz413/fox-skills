import copy
import json
import os
import subprocess
import sys
import tempfile
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('filter_context', Path(__file__).resolve().parents[1] / 'scripts/filter_context.py')
f = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f)


class FilterContextTests(unittest.TestCase):
    def setUp(self):
        self.data = {'goal': 'Diagnose a failed test', 'fragments': [
            {'id': 'required', 'source': 'log:1@v1', 'text': 'exit=1', 'required': True},
            {'id': 'counter', 'source': 'log:2@v1', 'text': 'Another run passed.', 'required': False},
            {'id': 'noise', 'source': 'doc:4@v1', 'text': 'Lunch menu', 'required': False}]}
        self.reply = {'model': f.MODEL, 'usage': {'input_tokens': 100, 'output_tokens': 2},
                      'answers': {'q1': {'type': 'noul', 'noul': 0.5}, 'q2': {'type': 'noul', 'noul': 0.999}}}

    def run_filter(self, **kwargs):
        return f.filter_context(self.data, key='test', evaluate=lambda *_: self.reply, **kwargs)

    def test_shadow_preserves_all_and_apply_copies_originals(self):
        original = copy.deepcopy(self.data)
        self.assertEqual(self.run_filter()['fragments'], self.data['fragments'])
        applied = self.run_filter(apply=True)
        self.assertEqual(applied['fragments'], self.data['fragments'][:2])
        self.assertEqual(applied['suggested_drop_ids'], ['noise'])
        self.assertEqual(self.data, original)
        self.assertNotIn('q0', f.make_request(self.data)['questions'])

    def test_invalid_response_falls_back_entire_input(self):
        for change in [lambda r: r['answers'].pop('q1'),
                       lambda r: r['answers'].update(q9={'type': 'noul', 'noul': 1}),
                       lambda r: r.update(model='other'),
                       lambda r: r.update(usage={}),
                       lambda r: r['answers']['q1'].update(type='choice')]:
            saved = copy.deepcopy(self.reply)
            change(self.reply)
            result = self.run_filter(apply=True)
            self.assertEqual(result['status'], 'fallback')
            self.assertEqual(result['fragments'], self.data['fragments'])
            self.reply = saved
        for value in [True, None, '0.99', float('nan'), float('inf'), -1, 2]:
            self.reply['answers']['q1']['noul'] = value
            self.assertEqual(self.run_filter(apply=True)['status'], 'fallback')

    def test_timeout_does_not_leak_exception_and_preserves_context(self):
        def fail(*_):
            raise TimeoutError('SECRET response body')
        result = f.filter_context(self.data, apply=True, key='test', evaluate=fail)
        self.assertEqual(result['fragments'], self.data['fragments'])
        self.assertNotIn('SECRET', str(result))
        self.assertEqual(result['reason'], 'TimeoutError')

    def test_local_guards_never_call_service(self):
        def fail(*_):
            self.fail('unexpected network call')
        self.assertEqual(f.filter_context(self.data, evaluate=fail)['reason'], 'missing_api_key')
        self.data['fragments'][1]['text'] = 'x' * f.MAX_REQUEST_BYTES
        self.assertEqual(f.filter_context(self.data, key='test', evaluate=fail)['reason'], 'request_too_large')
        for item in self.data['fragments']:
            item['required'] = True
        self.assertEqual(f.filter_context(self.data, key='test', evaluate=fail)['status'], 'skipped')

    def test_cli_fallback_exit_and_invalid_input(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'input.json'
            path.write_text(json.dumps(self.data))
            env = dict(os.environ)
            env.pop('TYPESAFE_API_KEY', None)
            command = [sys.executable, str(Path(f.__file__)), str(path), '--apply']
            result = subprocess.run(command, env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)['fragments'], self.data['fragments'])
            path.write_text('{invalid')
            result = subprocess.run(command, env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, '')
            self.assertEqual(path.read_text(), '{invalid')

    def test_bad_input_rejected_before_network(self):
        for change in [lambda d: d['fragments'][0].pop('required'),
                       lambda d: d['fragments'][1].update(id='required'),
                       lambda d: d.update(goal=''),
                       lambda d: d['fragments'][0].update(source='')]:
            data = copy.deepcopy(self.data)
            change(data)
            with self.assertRaises(ValueError):
                f.filter_context(data)


if __name__ == '__main__':
    unittest.main()
