# Actor 🐣

A tiny animated emoji companion for **macOS**, floating beside Codex.
Uses native Apple emoji, AppKit animation, and local activity signals. No server,
API key, screenshot access, or network connection required.

![Actor reacting to a live Codex session](assets/demo.gif)

## Install

### Download it

Grab `Actor-macOS.zip` from the
[latest release](https://github.com/mojtaba-borzu/actor-ai/releases/latest), unzip it
and move `Actor.app` into your Applications folder. One universal build, Apple Silicon
and Intel, macOS 13+.

The app is ad-hoc signed rather than notarized, and macOS quarantines anything a browser
downloaded, so it refuses to open until the flag is cleared:

```sh
xattr -dr com.apple.quarantine /Applications/Actor.app
```

To have it start at login, add it under System Settings -> General -> Login Items.

### Or build it

```sh
git clone https://github.com/mojtaba-borzu/actor-ai
cd actor-ai
python3 scripts/install.py
```

Requires macOS 13+ and Xcode Command Line Tools (`swiftc` and `/usr/bin/python3`).
Builds `~/Applications/Actor.app`, starts it and registers launch at login. It does
not change any coding-app configuration.

Building locally is the path with the least to trust: nothing is downloaded, so there
is no quarantine flag to clear and no login item to add by hand. Either way everything
Actor reads stays local; see [What is live](#what-is-live).

The background app shows its buddy when Codex / ChatGPT is open, or when
recent local coding events arrive. It hides when neither condition applies.
Open Actor once manually if you quit it before opening a coding app.

- **Drag** to choose a position; “Follow app position” restores automatic placement.
- **Click** for a heart. **Right-click** or use the menu bar emoji for settings.
- **Cat mood** changes the emoji palette.
- **Try a mood / Play all moods** previews animations, visibly labeled **Demo**.
- **Return to live** ends preview. Single previews expire after ten seconds.
- **Gentle motion** stops animation; macOS Reduce Motion is also respected.

| Mood | Meaning |
|---|---|
| 👋 | Arrival / goodbye |
| 🐣 | Ready |
| 🤔 | Thinking / reading |
| 🧑‍💻 | Editing / writing |
| 🛠️ | Calling a tool |
| 🥺 | Waiting for input or permission |
| 😵‍💫 | Reported failure |
| 🥳 | Turn completed |
| 😴 | Resting after inactivity |

Cat mood swaps the palette. Every mood, in order:

![All ten moods in the cat palette](assets/demo-cat.gif)

## What is live

**Codex:** reads local JSONL lifecycle/tool events from `$CODEX_HOME/sessions`
(default `~/.codex/sessions`). It tails recent files incrementally and never saves
conversation content. This works with the installed desktop build without changing
Codex config or requiring hook trust. The format is internal and may change.
Only observable states are shown: permission requests and tool-result failures
are **not reliably available** in these rollouts, so those Codex moods are currently
preview-only unless explicit error events arrive. Thinking is inferred between tools.

Auto mode follows the foreground supported app. For multiple Codex sessions, the
most recently observed prompt owns the state; activity in background sessions does
not continually steal focus. The initial focus search is bounded to 8 MB per recent
file, falling back to session creation time for older prompts. Exact selected-task
tracking inside the desktop UI is not exposed. Ten minutes without an activity
signal becomes “No recent signal”, never a false success. Status under the emoji
reads **Live**, **Ready** or **Demo**; the menu shows the event source.

State files contain only provider, mood, and timestamps under
`~/Library/Application Support/Actor`. Nothing is sent over the network.

## Develop / remove

```sh
./scripts/build.sh
python3 -m unittest discover -s tests -v
./tools/make-gif.sh Codex assets/demo.gif emoji demo
python3 scripts/install.py --uninstall
```

The demo GIFs are rendered by the app's own `draw()`, so they cannot drift from
what ships. `make-gif.sh` takes a provider label, an output path, `emoji` or
`cat`, and `demo` or `all`.

Uninstall removes only Actor's app and launch agent. It leaves small status files.

`proto/tauri/` is an experimental cross-platform shell: a Rust window that reads the
same `status.json` and renders the same moods in a webview, so Windows and Linux would
not need the AppKit view rewritten. It does not work off macOS yet — the shell and
`bridge.py` both resolve `~/Library/Application Support/Actor`, and the Codex reader is
macOS-only, so on another platform the window opens and never receives a state. Work on
it happens on the [`tauri-shell`](https://github.com/mojtaba-borzu/actor-ai/tree/tauri-shell)
branch. `tools/build-renderer.py` generates its UI by parsing the moods out of
`app/Actor.swift`, so the two cannot drift.

Integration reference: [Codex hooks and trust model](https://developers.openai.com/codex/hooks).

## License

[MIT](LICENSE). Apple emoji glyphs are rendered by the system font and are not
redistributed by this repository.
