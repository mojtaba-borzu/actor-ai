#!/usr/bin/env python3
"""Install the local macOS buddy and merge only Actor's Claude Code hooks."""
import argparse
import datetime
import json
import os
from pathlib import Path
import plistlib
import shlex
import shutil
import subprocess
import sys

REPO = Path(__file__).resolve().parent.parent
HOME = Path.home()
DEST = HOME / 'Applications/Actor.app'
AGENT = HOME / 'Library/LaunchAgents/local.actor.companion.plist'
SETTINGS = HOME / '.claude/settings.json'
MARKER = 'Actor.app/Contents/Resources/bridge.py'
sys.path.insert(0, str(REPO / 'app'))
from bridge import atomic_json, EVENTS


def merge_hooks(settings, remove=False):
    result = json.loads(json.dumps(settings))
    hooks = result.setdefault('hooks', {})
    for event, groups in list(hooks.items()):
        cleaned = []
        for group in groups:
            group = dict(group)
            group['hooks'] = [h for h in group.get('hooks', []) if MARKER not in h.get('command', '')]
            if group['hooks']:
                cleaned.append(group)
        if cleaned:
            hooks[event] = cleaned
        else:
            hooks.pop(event, None)
    if not remove:
        command = '/usr/bin/python3 ' + shlex.quote(str(DEST / 'Contents/Resources/bridge.py')) + ' hook --provider Claude'
        for event in list(EVENTS) + ['PreToolUse', 'Notification']:
            hooks.setdefault(event, []).append({'hooks': [{'type': 'command', 'command': command, 'timeout': 3}]})
    if not hooks:
        result.pop('hooks', None)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--uninstall', action='store_true')
    args = parser.parse_args()
    # Parse before changing anything: never replace an unreadable settings file.
    original = json.loads(SETTINGS.read_text()) if SETTINGS.exists() else {}
    merged = merge_hooks(original, args.uninstall)
    if not args.uninstall:
        subprocess.run([str(REPO / 'scripts/build.sh')], check=True)
    if SETTINGS.exists() and merged != original:
        backup = SETTINGS.with_name('settings.actor-backup-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f') + '.json')
        shutil.copy2(SETTINGS, backup)
    subprocess.run(['launchctl', 'bootout', 'gui/' + str(os.getuid()), str(AGENT)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # Stop only this app's executable, never the coding apps.
    subprocess.run(['pkill', '-f', '^' + str(DEST / 'Contents/MacOS/Actor') + '$'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if args.uninstall:
        atomic_json(SETTINGS, merged)
        AGENT.unlink(missing_ok=True)
        if DEST.exists():
            shutil.rmtree(DEST)
        print('Actor removed. Existing unrelated hooks and settings preserved.')
        return
    DEST.parent.mkdir(parents=True, exist_ok=True)
    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(REPO / '.build/Actor.app', DEST)
    atomic_json(SETTINGS, merged)
    AGENT.parent.mkdir(parents=True, exist_ok=True)
    with AGENT.open('wb') as out:
        plistlib.dump({'Label': 'local.actor.companion', 'ProgramArguments': [str(DEST / 'Contents/MacOS/Actor')], 'RunAtLoad': True, 'ProcessType': 'Interactive'}, out)
    subprocess.run(['launchctl', 'bootstrap', 'gui/' + str(os.getuid()), str(AGENT)], check=True)
    print('Installed:', DEST)
    print('Runs at login; appears while Claude/Codex is open or local coding events are active.')
    print('Claude Code hooks apply to new sessions. Codex uses local event files, without config changes.')

if __name__ == '__main__':
    main()
