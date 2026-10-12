import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from routing_eval import CASES, prompt, report, runtime_report
from cooperation_eval import report as cooperation_report


class RuntimeLegalityTests(unittest.TestCase):
    def setUp(self):
        self.inputs = {'runtime': {'m': {'efforts': ['low', 'medium']}},
                       'cases': [{'id': 'one', 'task': 'inert'}]}
        self.route = dict(id='one', status='requested', model='m',
                          reasoning_effort='medium', fork_turns='none', reason='evidence')

    def result(self, route=None, inputs=None):
        return runtime_report(inputs or self.inputs, [route or self.route])

    def test_unsupported_effort_and_case_patch(self):
        self.route['reasoning_effort'] = 'high'
        self.assertEqual(len(self.result()['violations']), 1)
        self.inputs['cases'][0]['runtime_patch'] = {'m': {'efforts': ['high']}}
        self.assertEqual(self.result()['passed'], 1)
        self.assertEqual(self.inputs['runtime']['m']['efforts'], ['low', 'medium'])

    def test_model_availability_and_compatibility(self):
        for metadata in (None, {'available': False}, {'compatible': False}):
            inputs = copy.deepcopy(self.inputs)
            if metadata is None:
                inputs['runtime'] = {}
            else:
                inputs['runtime']['m'].update(metadata)
            with self.subTest(metadata=metadata):
                self.assertEqual(len(self.result(inputs=inputs)['violations']), 1)

    def test_null_and_inherited_effort_controls(self):
        self.route['reasoning_effort'] = None
        self.assertTrue(self.result()['violations'])
        self.inputs['runtime']['m']['effort_control'] = 'unavailable'
        self.assertEqual(self.result()['passed'], 1)
        self.route['reasoning_effort'] = 'medium'
        self.assertTrue(self.result()['violations'])
        self.inputs['runtime']['m'].update(effort_control='inherited', inherited_effort='low')
        self.assertTrue(self.result()['violations'])
        self.route['reasoning_effort'] = 'low'
        self.assertEqual(self.result()['passed'], 1)

    def test_unselected_and_missing_runtime_not_claimed_valid(self):
        self.route.update(status='blocked', model=None, reasoning_effort=None)
        result = self.result()
        self.assertEqual(result['checked'], 0)
        self.assertEqual(len(result['not_checked']), 1)
        self.route['model'] = 'm'
        self.assertTrue(self.result()['violations'])
        self.inputs.pop('runtime')
        self.assertEqual(self.result()['checked'], 0)

    def test_unknown_inherited_effort_needs_review(self):
        self.route.update(status='inherited', reasoning_effort=None)
        result = self.result()
        self.assertEqual(result['checked'], 0)
        self.assertEqual(len(result['not_checked']), 1)
        self.assertEqual(result['violations'], [])

    def test_explicit_model_with_unknown_inherited_effort_needs_review(self):
        self.route['reasoning_effort'] = None
        for explicit_null in (False, True):
            model = {'efforts': ['low', 'medium'], 'effort_control': 'inherited'}
            if explicit_null:
                model['inherited_effort'] = None
            self.inputs['cases'][0]['runtime_patch'] = {'m': model}
            with self.subTest(explicit_null=explicit_null):
                result = self.result()
                self.assertEqual(result['passed'], 0)
                self.assertEqual(result['checked'], 0)
                self.assertEqual(len(result['not_checked']), 1)
                self.assertEqual(result['violations'], [])
        self.inputs['cases'][0]['runtime_patch']['m']['inherited_effort'] = 'medium'
        self.route['reasoning_effort'] = 'medium'
        self.assertEqual(self.result()['passed'], 1)

    def test_invalid_structure_or_coverage_unscored(self):
        for items in ([], [self.route, self.route], [{}]):
            result = runtime_report(self.inputs, items)
            self.assertIsNone(result['passed'])
            self.assertTrue(result['errors'])

    def test_all_fixed_expectations_obey_runtime(self):
        suite = json.loads(CASES.read_text())
        predictions = [dict(id=c['id'], reason='fixture', **c['expected']) for c in suite['cases']]
        self.assertEqual(runtime_report(prompt(suite), predictions)['violations'], [])

    def test_legality_is_separate_from_expectation_match(self):
        suite = dict(self.inputs)
        suite['cases'] = [dict(self.inputs['cases'][0], group='rules',
                               expected={'status': 'requested', 'model': 'm',
                                         'reasoning_effort': 'low', 'fork_turns': 'none'})]
        result = report(suite, [self.route])
        self.assertEqual(result['runtime_validity']['passed'], 1)
        self.assertEqual(result['groups']['rules']['passed'], 0)
        self.assertEqual(len(result['expectation_differences_without_runtime_violation']), 1)
        self.route['reasoning_effort'] = 'high'
        result = report(suite, [self.route])
        self.assertEqual(len(result['runtime_validity']['violations']), 1)
        self.assertEqual(result['expectation_differences_without_runtime_violation'], [])

    def test_cooperation_uses_same_runtime_check(self):
        self.route['reasoning_effort'] = 'high'
        item = dict(id='one', action='delegate', role='worker', context='supplied',
                    route=self.route, reason='evidence')
        suite = {'cases': [dict(id='one', expected={k: v for k, v in item.items() if k not in ('id', 'reason')})]}
        result = cooperation_report(suite, [item], self.inputs['runtime'])
        self.assertEqual(len(result['runtime_validity']['violations']), 1)

    def test_public_runtime_cli_needs_no_expected_answers(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / 'routing_eval.py'
            script.write_text(Path(__file__).with_name('routing_eval.py').read_text())
            inputs, predictions = Path(tmp) / 'inputs.json', Path(tmp) / 'predictions.json'
            inputs.write_text(json.dumps(self.inputs))
            predictions.write_text(json.dumps([self.route]))
            command = [sys.executable, str(script), str(predictions), '--validate-runtime', str(inputs)]
            run = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.route['reasoning_effort'] = 'high'
            predictions.write_text(json.dumps([self.route]))
            run = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertTrue(json.loads(run.stdout)['violations'])


if __name__ == '__main__':
    unittest.main()
