import copy
import json
import unittest
from cooperation_eval import ACTIONS, CASES, prompt, report, validate_output


class CooperationTests(unittest.TestCase):
    def setUp(self):
        self.suite = json.loads(CASES.read_text())
        self.answers = []
        for case in self.suite['cases']:
            answer = dict(id=case['id'], reason='evidence', **copy.deepcopy(case['expected']))
            if answer['route']:
                answer['route']['reason'] = 'task-specific routing evidence'
            self.answers.append(answer)

    def test_expected_routes_and_free_reasons(self):
        self.assertEqual(report(self.suite, self.answers)['cooperation']['passed'], len(self.answers))

    def test_hidden_expectations(self):
        output = prompt(self.suite, {})
        self.assertTrue(all(set(c) == {'id', 'task'} for c in output['cases']))

    def test_history_inheritance_rejected_by_score(self):
        answer = next(a for a in self.answers if a['role'] == 'advisor' and a['route'])
        answer['route']['fork_turns'] = 'all'
        self.assertEqual(report(self.suite, self.answers)['cooperation']['passed'], len(self.answers) - 1)

    def test_no_route_for_local_or_followup(self):
        self.answers[0]['route'] = copy.deepcopy(self.answers[2]['route'])
        self.answers[0]['route']['id'] = self.answers[0]['id']
        self.assertEqual(report(self.suite, self.answers)['cooperation']['passed'], len(self.answers) - 1)

    def test_invalid_structure_or_coverage_unscored(self):
        for items in (self.answers[:-1], self.answers + [self.answers[0]], ['bad']):
            self.assertIsNone(report(self.suite, items)['cooperation']['passed'])

    def test_nested_route_validation(self):
        self.answers[2]['route']['fork_turns'] = 'because it needs history'
        self.assertTrue(validate_output(self.answers))

    def test_prompt_defines_every_action_without_expected_answers(self):
        contract = prompt(self.suite, {})['contract']
        self.assertEqual(set(contract['action_meanings']), set(contract['actions']))
        self.assertTrue(all(isinstance(v, str) and v.strip() for v in ACTIONS.values()))

    def test_standalone_prompt_contains_complete_route_contract(self):
        contract = prompt(self.suite, {})['contract']['route_contract']
        self.assertEqual(set(contract['required_fields']),
                         {'id', 'status', 'model', 'reasoning_effort', 'fork_turns', 'reason'})
        self.assertEqual(set(contract['status']), {'requested', 'inherited', 'blocked'})

    def test_repair_owner_then_independent_reviewer(self):
        case = next(c for c in self.suite['cases'] if c['id'] == 'case_c05')
        answer = dict(id=case['id'], action='repair_recheck', role='worker',
                      context='retained', route=None,
                      reason='Existing worker repairs its resource, then the independent reviewer rechecks affected behavior.')
        self.assertEqual(report({'cases': [case]}, [answer])['cooperation']['passed'], 1)
        answer['role'] = 'reviewer'
        self.assertEqual(report({'cases': [case]}, [answer])['cooperation']['passed'], 0)

    def test_malformed_field_values_do_not_crash(self):
        for field in ('id', 'action', 'role', 'context', 'route', 'reason'):
            for value in ([], {}, 42, True):
                bad = copy.deepcopy(self.answers)
                bad[0][field] = value
                with self.subTest(field=field, value=value):
                    result = report(self.suite, bad)
                    self.assertFalse(result['structure']['passed'])
                    self.assertIsNone(result['cooperation']['passed'])

    def test_nested_error_identifies_parent_row(self):
        self.answers[2]['route']['status'] = 'invalid'
        self.assertTrue(any(error.startswith('2: route:') for error in validate_output(self.answers)))

    def test_wrong_action_fails(self):
        self.answers[0]['action'] = 'consult'
        self.assertEqual(report(self.suite, self.answers)['cooperation']['passed'], len(self.answers) - 1)


if __name__ == '__main__':
    unittest.main()
