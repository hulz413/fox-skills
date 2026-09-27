import copy
import json
import unittest
from cooperation_eval import CASES, prompt, report, validate_output


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

    def test_wrong_action_fails(self):
        self.answers[0]['action'] = 'consult'
        self.assertEqual(report(self.suite, self.answers)['cooperation']['passed'], len(self.answers) - 1)


if __name__ == '__main__':
    unittest.main()
