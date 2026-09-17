import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'app'))
from bridge import Tail, Monitor, emit, hook_state, rollout_state, latest_start
spec = importlib.util.spec_from_file_location('installer', Path(__file__).resolve().parents[1] / 'scripts/install.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)

class BridgeTests(unittest.TestCase):
    def test_real_codex_lifecycle(self):
        for kind, expected in [('task_started', 'thinking'), ('task_complete', 'success'), ('turn_aborted', 'idle')]:
            self.assertEqual(rollout_state({'type': 'event_msg', 'payload': {'type': kind}}), expected)
        self.assertEqual(rollout_state({'type':'response_item','payload':{'type':'custom_tool_call','name':'apply_patch'}}), 'working')
        self.assertIsNone(rollout_state({'type':'event_msg','payload':{'type':'token_count'}}))

    def test_focus_recovers_across_large_tool_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'large.jsonl'
            start = {'timestamp':'2026-09-17T12:00:00Z','type':'event_msg','payload':{'type':'task_started'}}
            path.write_text(json.dumps(start)+'\n'+json.dumps({'type':'response_item','payload':{'type':'custom_tool_call_output','output':'x'*700000}})+'\n')
            self.assertGreater(latest_start(path), 0)

    def test_claude_permission_and_failure(self):
        self.assertEqual(hook_state({'hook_event_name':'PermissionRequest'}), 'waiting')
        self.assertEqual(hook_state({'hook_event_name':'PostToolUseFailure'}), 'error')
        self.assertEqual(hook_state({'hook_event_name':'Notification','notification_type':'permission_prompt'}), 'waiting')
        self.assertIsNone(hook_state({'hook_event_name':'Notification','notification_type':'other'}))

    def test_partial_tail_and_truncation(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'events.jsonl'; tail = Tail()
            path.write_bytes(b'{"a":1}\n{"b":')
            self.assertEqual(tail.read(path), [{'a':1}])
            with path.open('ab') as f: f.write(b'2}\n')
            self.assertEqual(tail.read(path), [{'b':2}])
            self.assertEqual(tail.read(path), [])
            path.write_text('{"c":3}\n')
            self.assertEqual(tail.read(path), [{'c':3}])

    def test_no_content_leak_and_child_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            emit('Claude', {'hook_event_name':'UserPromptSubmit','session_id':'../bad','prompt':'secret'}, root)
            files = list((root/'events').glob('*.json'))
            self.assertEqual(len(files),1)
            self.assertNotIn('secret', files[0].read_text())
            emit('Claude', {'hook_event_name':'Stop','session_id':'../bad','agent_id':'child'}, root)
            self.assertEqual(json.loads(files[0].read_text())['state'], 'thinking')

    def test_focused_session_and_staleness(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); monitor = Monitor(root=root, codex=root/'none'); now=time.time()
            monitor.sessions = {
                ('Codex','a'): dict(provider='Codex',state='working',start=now-20,at=now,source='Local events'),
                ('Codex','b'): dict(provider='Codex',state='success',start=now-10,at=now-2,source='Local events')}
            self.assertEqual(monitor.poll(now)['Codex']['state'], 'success')
            self.assertEqual(monitor.poll(now+5)['Codex']['state'], 'idle')
            monitor.sessions[('Codex','b')]['state'] = 'thinking'
            result = monitor.poll(now+700)['Codex']
            self.assertEqual(result['state'], 'idle')
            self.assertEqual(result['source'], 'No recent signal')

    def test_install_merge_idempotent_and_uninstall_preserves_others(self):
        original = {'theme':'dark','hooks':{'Stop':[{'matcher':'x','hooks':[{'type':'command','command':'echo unrelated'}]}]}}
        merged = installer.merge_hooks(original)
        self.assertEqual(installer.merge_hooks(merged), merged)
        self.assertEqual(installer.merge_hooks(merged, True), original)
        self.assertEqual(original['hooks']['Stop'][0]['hooks'][0]['command'], 'echo unrelated')

if __name__ == '__main__': unittest.main()
