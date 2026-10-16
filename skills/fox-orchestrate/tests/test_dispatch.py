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

    def test_fresh_context_does_not_replace_model_and_effort_selection(self):
        calls = [dict(task_name=name, fork_turns='none') for name in ('extract', 'compare')]
        self.assertTrue(check(calls, {'efficient-test-model'}))

    def test_actual_calls_must_match_each_selected_effort(self):
        expected = {'extract': self.good(), 'compare': {**self.good(), 'reasoning_effort': 'medium'}}
        calls = [dict(task_name=name, **route) for name, route in expected.items()]
        self.assertEqual(check(calls, {'efficient-test-model'}, expected), [])
        calls[1]['reasoning_effort'] = 'low'
        self.assertTrue(check(calls, {'efficient-test-model'}, expected))
        calls[1] = calls[0]
        self.assertTrue(check(calls, {'efficient-test-model'}, expected))

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

    def test_malformed_calls_return_errors(self):
        self.assertTrue(check([None, self.good()], {'efficient-test-model'}))
        for field, value in [('model', []), ('model', {}), ('fork_turns', '²'),
                             ('fork_turns', {}), ('reasoning_effort', [])]:
            call = self.good(); call[field] = value
            with self.subTest(field=field, value=value):
                self.assertTrue(check([call, self.good()], {'efficient-test-model'}))

    def test_limited_history_uses_shared_syntax(self):
        for value in ('2', '1' * 5000):
            call = self.good(); call['fork_turns'] = value
            self.assertEqual(check([call, self.good()], {'efficient-test-model'}), [])

    def test_reads_actual_call_not_text_claims(self):
        records = [
            {'type': 'response_item', 'payload': {'type': 'message', 'text': 'I used efficient models'}},
            {'type': 'response_item', 'payload': {'type': 'function_call', 'name': 'collaboration.spawn_agent', 'arguments': json.dumps(self.good())}},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'trace.jsonl'
            path.write_text('\n'.join(map(json.dumps, records)))
            self.assertEqual(list(dispatches(path)), [self.good()])

    def test_current_tool_and_task_scope_cannot_hide_missing_calls(self):
        expected = {'extract': self.good(), 'compare': self.good()}
        records = [
            {'type': 'response_item', 'payload': {
                'type': 'function_call', 'name': tool,
                'arguments': json.dumps(dict(task_name=name, **self.good()))}}
            for tool, name in [('collaboration.start_delegated_task', 'extract'),
                               ('spawn_agent', 'compare'), ('spawn_agent', 'unrelated')]
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'trace.jsonl'
            path.write_text('\n'.join(map(json.dumps, records)))
            calls = list(dispatches(path, expected))
            self.assertEqual(check(calls, {'efficient-test-model'}, expected), [])
            self.assertTrue(check(list(dispatches(path, {'missing'})), {'efficient-test-model'}, expected))

    def test_cli_rejects_old_inheritance_and_binds_actual_routes(self):
        import subprocess
        import sys
        expected = {'extract': self.good(), 'compare': {**self.good(), 'reasoning_effort': 'medium'}}
        with tempfile.TemporaryDirectory() as tmp:
            path, plan = Path(tmp)/'trace.jsonl', Path(tmp)/'routes.json'
            plan.write_text(json.dumps(expected))
            calls = [dict(task_name=name, fork_turns='none') for name in expected]
            command = [sys.executable, str(Path(__file__).with_name('check_dispatch.py')), str(path),
                       '--efficient-model', 'efficient-test-model', '--expectations', str(plan)]
            for explicit, code in ((False, 1), (True, 0)):
                if explicit:
                    calls = [dict(task_name=name, **route) for name, route in expected.items()]
                records = [{'type': 'response_item', 'payload': {'type': 'function_call',
                            'name': 'spawn_agent', 'arguments': json.dumps(call)}} for call in calls]
                path.write_text('\n'.join(map(json.dumps, records)))
                run = subprocess.run(command, capture_output=True, text=True)
                self.assertEqual(run.returncode, code, run.stderr)


if __name__ == '__main__':
    unittest.main()
