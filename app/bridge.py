"""Local-only event bridge. Never persists prompts, tool arguments or responses."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import tempfile
import time

ROOT = Path.home() / 'Library/Application Support/Actor'
STATES = {'idle', 'appear', 'thinking', 'working', 'tool', 'waiting', 'error', 'success', 'sleep', 'goodbye'}
EVENTS = {
    'SessionStart': 'appear', 'UserPromptSubmit': 'thinking',
    'PostToolUse': 'thinking', 'PostToolUseFailure': 'error',
    'PermissionRequest': 'waiting', 'Stop': 'success', 'StopFailure': 'error',
    'SessionEnd': 'goodbye', 'PreCompact': 'thinking', 'PostCompact': 'thinking',
}

def tool_state(name):
    name = name.lower()
    if any(x in name for x in ('read', 'search', 'grep', 'glob', 'find', 'list')):
        return 'thinking'
    if any(x in name for x in ('edit', 'write', 'patch')):
        return 'working'
    return 'tool'

def hook_state(data):
    event = data.get('hook_event_name')
    if event == 'PreToolUse':
        return tool_state(data.get('tool_name', ''))
    if event == 'Notification':
        return 'waiting' if data.get('notification_type') in ('permission_prompt', 'elicitation_dialog', 'agent_needs_input') else None
    return EVENTS.get(event)

def rollout_state(data):
    payload = data.get('payload', {})
    kind = payload.get('type')
    if data.get('type') == 'event_msg':
        return {'task_started': 'thinking', 'task_complete': 'success',
                'turn_aborted': 'idle', 'error': 'error'}.get(kind)
    if data.get('type') == 'response_item':
        if kind in ('function_call', 'custom_tool_call'):
            return tool_state(payload.get('name', ''))
        if kind in ('function_call_output', 'custom_tool_call_output', 'reasoning'):
            return 'thinking'
    return None

def atomic_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as out:
            json.dump(data, out)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)

class Tail:
    """Incremental bounded reads; incomplete lines are retried on the next poll."""
    def __init__(self):
        self.offset = 0
        self.identity = None

    def read(self, path):
        stat = path.stat()
        identity = (stat.st_dev, stat.st_ino)
        first = self.identity != identity or stat.st_size < self.offset
        if first:
            self.offset = max(0, stat.st_size - 512 * 1024)
            self.identity = identity
        result = []
        with path.open('rb') as stream:
            stream.seek(self.offset)
            if first and self.offset:
                stream.readline()  # discard potentially partial first record
            while stream.tell() - self.offset < 2 * 1024 * 1024:
                pos = stream.tell()
                line = stream.readline()
                if not line or not line.endswith(b'\n'):
                    stream.seek(pos)
                    break
                try:
                    result.append(json.loads(line))
                except (ValueError, UnicodeDecodeError):
                    pass
            self.offset = stream.tell()
        return result

def timestamp(value):
    try:
        return dt.datetime.fromisoformat(value.replace('Z', '+00:00')).timestamp()
    except (ValueError, TypeError, AttributeError):
        return 0

def latest_start(path):
    """Recover focus on launch even when a large tool result filled the tail."""
    with path.open('rb') as stream:
        stream.seek(0, 2)
        end = stream.tell()
        carry = b''
        remaining = 8 * 1024 * 1024
        while end and remaining > 0:
            size = min(end, 256 * 1024, remaining)
            end -= size
            remaining -= size
            stream.seek(end)
            parts = (stream.read(size) + carry).split(b'\n')
            carry = parts.pop(0) if end else b''
            for line in reversed(parts):
                if b'"task_started"' not in line:
                    continue
                try:
                    record = json.loads(line)
                    if record.get('type') == 'event_msg' and record.get('payload', {}).get('type') == 'task_started':
                        return timestamp(record.get('timestamp'))
                except (ValueError, UnicodeDecodeError):
                    pass
        # A session's creation is a conservative fallback if its prompt is older
        # than the bounded scan. New task_started events will replace it live.
        stream.seek(0)
        try:
            return timestamp(json.loads(stream.readline()).get('timestamp'))
        except (ValueError, UnicodeDecodeError):
            return 0

class Monitor:
    def __init__(self, root=ROOT, codex=None):
        self.root = root
        self.codex = codex or Path(os.environ.get('CODEX_HOME', str(Path.home()/'.codex'))) / 'sessions'
        self.tails = {}
        self.sessions = {}
        self.files = []
        self.next_scan = 0

    def poll(self, now=None):
        now = now or time.time()
        if now >= self.next_scan:
            self.next_scan = now + 4
            # Only today/yesterday: do not recursively scan all historical conversations.
            days = [dt.datetime.now() - dt.timedelta(days=i) for i in range(2)]
            candidates = []
            for day in days:
                directory = self.codex / day.strftime('%Y/%m/%d')
                if directory.exists():
                    candidates.extend(directory.glob('*.jsonl'))
            self.files = sorted(candidates, key=lambda p: p.stat().st_mtime, reverse=True)[:24]
        for path in self.files:
            try:
                if path not in self.tails:
                    self.tails[path] = Tail()
                    self.sessions[('Codex', str(path))] = dict(provider='Codex', state='idle', at=0, start=latest_start(path), source='Local events')
                for record in self.tails[path].read(path):
                    state = rollout_state(record)
                    if not state:
                        continue
                    at = timestamp(record.get('timestamp'))
                    key = ('Codex', str(path))
                    prev = self.sessions.get(key, {})
                    start = at if record.get('payload', {}).get('type') == 'task_started' else prev.get('start', 0)
                    self.sessions[key] = dict(provider='Codex', state=state, at=at, start=start, source='Local events')
            except (OSError, ValueError):
                continue
        for path in (self.root / 'events').glob('*.json'):
            try:
                record = json.loads(path.read_text())
                if record.get('state') in STATES and record.get('provider') in ('Claude', 'Codex'):
                    if now - record.get('at', 0) < 86400:
                        self.sessions[(record['provider'], path.name)] = record
                    else:
                        path.unlink(missing_ok=True)
            except (OSError, ValueError, TypeError):
                continue
        output = {}
        for provider in ('Codex', 'Claude'):
            records = [r for r in self.sessions.values() if r['provider'] == provider and now-r['at'] < 86400]
            if not records:
                continue
            # Most recently prompted session owns the mascot, not the noisiest tool.
            selected = max(records, key=lambda r: (r.get('start', 0), r['at']))
            selected = dict(selected)
            age = now - selected['at']
            if selected['state'] in ('success', 'appear', 'goodbye') and age > 4:
                selected['state'] = 'idle'
            if selected['state'] == 'idle' and age > 90:
                selected['state'] = 'sleep'
            # Silence is not success or an error: explicitly mark stale activity unknown.
            if selected['state'] in ('working', 'tool', 'thinking', 'waiting') and age > 600:
                selected['state'] = 'idle'
                selected['source'] = 'No recent signal'
            output[provider] = selected
        atomic_json(self.root / 'status.json', output)
        return output

def emit(provider, data, root=ROOT):
    state = hook_state(data)
    if state is None:
        return
    # Child agents should not overwrite their parent's visible status.
    if data.get('agent_id'):
        return
    session = str(data.get('session_id', 'default'))
    key = hashlib.sha256((provider + session).encode()).hexdigest()[:24]
    path = root / 'events' / (key + '.json')
    now = time.time()
    start = now
    try:
        start = json.loads(path.read_text()).get('start', now)
    except (OSError, ValueError):
        pass
    if data.get('hook_event_name') in ('SessionStart', 'UserPromptSubmit'):
        start = now
    atomic_json(path, dict(provider=provider, state=state, at=now, start=start, source='Live hooks'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=('monitor', 'hook'))
    parser.add_argument('--provider', choices=('Claude', 'Codex'), default='Claude')
    args = parser.parse_args()
    if args.mode == 'hook':
        import sys
        try:
            emit(args.provider, json.load(sys.stdin))
        except (OSError, ValueError, TypeError):
            pass  # Visual-only hooks must never block an agent or write to stdout.
    else:
        monitor = Monitor()
        parent = os.getppid()
        while os.getppid() == parent:
            try:
                monitor.poll()
            except OSError:
                pass
            time.sleep(0.6)
