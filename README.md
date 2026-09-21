# Actor 🐣

A tiny animated emoji companion for **macOS**, floating beside Codex.
Uses native Apple emoji, AppKit animation, and local activity signals. No server,
API key, screenshot access, or network connection required.

> **This branch carries the experimental cross-platform shell.** The shipping app is
> the AppKit one on [`main`](https://github.com/mojtaba-borzu/actor-ai/tree/main).
> Everything below describes that app; [Cross-platform shell](#cross-platform-shell)
> covers what this branch adds and what it still cannot do.

![Actor reacting to a live Codex session](assets/demo.gif)

## Install

```sh
git clone https://github.com/mojtaba-borzu/actor-ai
cd actor-ai
python3 scripts/install.py
```

Requires macOS 13+ and Xcode Command Line Tools (`swiftc` and `/usr/bin/python3`).
Builds `~/Applications/Actor.app`, starts it and registers launch at login. It does
not change any coding-app configuration.

Actor is compiled on your own machine from the source in this repository, so there
is no prebuilt binary to trust and no Gatekeeper warning to click past. Everything
it reads stays local; see [What is live](#what-is-live).

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

Integration reference: [Codex hooks and trust model](https://developers.openai.com/codex/hooks).

## Cross-platform shell

`proto/tauri/` is a Rust and Tauri v2 window that reads the same `status.json` the
macOS app writes and renders the same moods in a webview, so Windows and Linux would
not need the AppKit view rewritten.

```sh
cd proto/tauri
cargo run
```

Requires a Rust toolchain. On Linux, Tauri v2 additionally needs the webkit2gtk and
libappindicator development packages.

Working: the transparent, always-on-top, click-through-free window; the native context
menu, rebuilt in Rust on every right-click so its check marks and status line are never
stale; dragging past a 4 px threshold, which keeps click-for-a-heart alive the way the
AppKit view does; the appearance and size submenus; mood previews.

**Not working off macOS.** `status_path()` in `src/main.rs` resolves
`$HOME/Library/Application Support/Actor/status.json`, and `bridge.py` writes to that
same macOS path, so elsewhere the window opens and never receives a state. Making it
real needs a per-platform data directory on both sides and a Codex session reader that
is not macOS-only. Until then this is a prototype that happens to run on macOS.

Tauri v2 grants no permissions by default; `capabilities/default.json` is what lets the
window listen for events, drag and resize itself. Transparency relies on
`macOSPrivateApi`, which rules out the Mac App Store.

`tools/build-renderer.py` generates `ui/index.html` by parsing the moods out of
`app/Actor.swift`, so the renderer cannot drift from the shipped app. Edit the poses
there and rerun it.

## License

[MIT](LICENSE). Apple emoji glyphs are rendered by the system font and are not
redistributed by this repository.
