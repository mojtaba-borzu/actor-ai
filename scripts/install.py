#!/usr/bin/env python3
"""Install the local macOS buddy. Touches no coding-app configuration."""
import argparse
import os
from pathlib import Path
import plistlib
import shutil
import subprocess

REPO = Path(__file__).resolve().parent.parent
HOME = Path.home()
DEST = HOME / 'Applications/Actor.app'
AGENT = HOME / 'Library/LaunchAgents/local.actor.companion.plist'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--uninstall', action='store_true')
    args = parser.parse_args()
    if not args.uninstall:
        subprocess.run([str(REPO / 'scripts/build.sh')], check=True)
    subprocess.run(['launchctl', 'bootout', 'gui/' + str(os.getuid()), str(AGENT)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # Stop only this app's executable, never the coding apps.
    subprocess.run(['pkill', '-f', '^' + str(DEST / 'Contents/MacOS/Actor') + '$'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if args.uninstall:
        AGENT.unlink(missing_ok=True)
        if DEST.exists():
            shutil.rmtree(DEST)
        print('Actor removed.')
        return
    DEST.parent.mkdir(parents=True, exist_ok=True)
    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(REPO / '.build/Actor.app', DEST)
    AGENT.parent.mkdir(parents=True, exist_ok=True)
    with AGENT.open('wb') as out:
        plistlib.dump({'Label': 'local.actor.companion', 'ProgramArguments': [str(DEST / 'Contents/MacOS/Actor')], 'RunAtLoad': True, 'ProcessType': 'Interactive'}, out)
    subprocess.run(['launchctl', 'bootstrap', 'gui/' + str(os.getuid()), str(AGENT)], check=True)
    print('Installed:', DEST)
    print('Runs at login; appears while Codex is open or local coding events are active.')
    print('Codex uses local event files, without config changes.')

if __name__ == '__main__':
    main()
