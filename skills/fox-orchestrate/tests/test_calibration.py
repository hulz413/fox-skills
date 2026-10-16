"""Baseline preferences must not weaken pins, controls or cooperation boundaries."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import routing_eval as routing
import cooperation_eval as cooperation


class CalibrationTests(unittest.TestCase):
    def setUp(self):
        self.suite = json.loads(routing.CASES.read_text())
        self.answers = [dict(id=c['id'], reason='Synthetic checker replay', **c['expected'])
                        for c in self.suite['cases']]

    def change(self, case_id, **changes):
        next(row for row in self.answers if row['id'] == case_id).update(changes)
        return routing.report(self.suite, self.answers)

    def test_ambiguous_effort_remains_a_baseline_difference(self):
        result = self.change('case_016', reasoning_effort='xhigh')
        self.assertEqual(result['groups']['rules']['total'] - result['groups']['rules']['passed'], 1)
        self.assertFalse(routing.automatic_failure(result))
        self.assertEqual(result['constraints']['calibration_differences'],
                         [{'id': 'case_016', 'fields': ['reasoning_effort']}])

    def test_calibration_cannot_allow_unsupported_settings(self):
        result = self.change('case_033', reasoning_effort='max')
        self.assertTrue(result['runtime_validity']['violations'])
        self.assertTrue(routing.automatic_failure(result))

    def test_pins_inheritance_controls_and_fallback_remain_required(self):
        changes = [('case_009', {'reasoning_effort': 'high'}),
                   ('case_013', {'model': 'standard-fixture'}),
                   ('case_012', {'fork_turns': 'none'}),
                   ('case_043', {'reasoning_effort': 'low'}),
                   ('case_017', {'reasoning_effort': 'ultra'}),
                   ('case_054', {'model': 'current-fixture'}),
                   ('case_061', {'status': 'requested', 'model': 'light-fixture', 'reasoning_effort': 'low'})]
        for case_id, fields in changes:
            with self.subTest(case=case_id):
                answers = copy.deepcopy(self.answers)
                next(row for row in answers if row['id'] == case_id).update(fields)
                self.assertTrue(routing.automatic_failure(routing.report(self.suite, answers)))

    def test_calibration_metadata_is_hidden_and_limited_to_settings(self):
        self.assertTrue(all('calibration_fields' not in case for case in routing.prompt(self.suite)['cases']))
        for case in self.suite['cases']:
            fields = case.get('calibration_fields', [])
            self.assertLessEqual(set(fields), {'model', 'reasoning_effort'})
            self.assertEqual(len(fields), len(set(fields)))

    def test_cli_gates_constraints_and_reports_preferences(self):
        script = str(Path(routing.__file__).resolve())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'predictions.json'
            next(row for row in self.answers if row['id'] == 'case_016')['reasoning_effort'] = 'xhigh'
            path.write_text(json.dumps(self.answers))
            command = [sys.executable, script, str(path)]
            run = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertTrue(json.loads(run.stdout)['constraints']['calibration_differences'])
            next(row for row in self.answers if row['id'] == 'case_009')['reasoning_effort'] = 'high'
            path.write_text(json.dumps(self.answers))
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)

    def test_cooperation_preferences_do_not_relax_actions_or_advisor_context(self):
        suite = json.loads(cooperation.CASES.read_text())
        answers = [dict(id=c['id'], reason='Synthetic replay', **copy.deepcopy(c['expected']))
                   for c in suite['cases']]
        for row in answers:
            if row['route']:
                row['route']['reason'] = 'Independent route reason'
        advisor = next(row for row in answers if row['id'] == 'case_c07')
        advisor['route']['reasoning_effort'] = 'xhigh'
        result = cooperation.report(suite, answers, self.suite['runtime'])
        self.assertEqual(result['constraints']['errors'], [])
        self.assertTrue(result['constraints']['calibration_differences'])
        self.assertEqual(result['cooperation']['passed'], len(answers) - 1)
        advisor['route']['fork_turns'] = 'all'
        self.assertTrue(cooperation.report(suite, answers, self.suite['runtime'])['constraints']['errors'])
        advisor['route']['fork_turns'] = 'none'
        advisor['action'] = 'local'
        self.assertFalse(cooperation.report(suite, answers, self.suite['runtime'])['structure']['passed'])


if __name__ == '__main__':
    unittest.main()
