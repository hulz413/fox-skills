import json
import tempfile
import unittest
from pathlib import Path
from check_dispatch import check, dispatches


class DispatchTests(unittest.TestCase):
    def good(self):
        return dict(model='efficient-test-model', reasoning_effort='low', fork_turns='none')

    def test_explicit_dispatch(self):
        self.assertEqual(check([self.good(), self.good()], {'efficient-test-model'}), [])

    def test_original_silent_inheritance_regression(self):
        self.assertTrue(check([{'task_name': 'a'}, {'task_name': 'b'}], {'efficient-test-model'}))

    def test_no_dispatch_is_not_a_pass(self):
        self.assertTrue(check([], {'efficient-test-model'}))

    def test_full_history_with_overrides(self):
        call = self.good(); call.pop('fork_turns')
        self.assertTrue(check([call, self.good()], {'efficient-test-model'}))

    def test_missing_effort(self):
        call = self.good(); call.pop('reasoning_effort')
        self.assertTrue(check([call, self.good()], {'efficient-test-model'}))

    def test_explicit_frontier_for_every_trivial_task(self):
        call = self.good(); call['model'] = 'frontier-test-model'
        self.assertTrue(check([call, call], {'efficient-test-model'}))

    def test_reads_actual_call_not_text_claims(self):
        records = [
            {'type': 'response_item', 'payload': {'type': 'message', 'text': 'I used efficient models'}},
            {'type': 'response_item', 'payload': {'type': 'function_call', 'name': 'collaboration.spawn_agent', 'arguments': json.dumps(self.good())}},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'trace.jsonl'
            path.write_text('\n'.join(map(json.dumps, records)))
            self.assertEqual(list(dispatches(path)), [self.good()])


if __name__ == '__main__':
    unittest.main()
