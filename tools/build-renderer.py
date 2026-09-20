#!/usr/bin/env python3
"""Generates the cross-platform renderer for proto/tauri.

Moods, emoji and captions are parsed out of app/Actor.swift, so the web renderer
cannot drift from the shipped macOS app. Edit the poses there, rerun this.
"""
import ast, pathlib, re

root = pathlib.Path(__file__).resolve().parent.parent
swift = (root / 'app/Actor.swift').read_text()

def poses():
    block = re.search(r'let poses: \[String: \(String, String, String\)\] = \[(.*?)\n\]', swift, re.S).group(1)
    out = {}
    for key, emoji, caption, sparkle in re.findall(
            r'"(\w+)":\s*\("([^"]*)",\s*"([^"]*)",\s*"([^"]*)"\)', block):
        out[key] = (emoji, caption, sparkle)
    return out

def cats():
    block = re.search(r'let cats = \[(.*?)\]', swift, re.S).group(1)
    return dict(re.findall(r'"(\w+)":\s*"([^"]*)"', block))

def ordered():
    block = re.search(r'let orderedStates = \[(.*?)\]', swift, re.S).group(1)
    return re.findall(r'"(\w+)"', block)

POSES, CATS, ORDER = poses(), cats(), ordered()
missing = [s for s in ORDER if s not in POSES or s not in CATS]
assert not missing, 'Actor.swift is missing poses/cats for: ' + ', '.join(missing)

CSS = """
/* Sizes are in vh/vw so resizing the window IS the size setting: no second
   scale factor to keep in step with the Rust side. */
/* Animation pacing lives here: one place to speed the whole character up or down. */
:root{--bob:1.8s;--blink:.85s;--hop:.42s;--wobble:.32s;--doze:3.8s}
html,body{margin:0;height:100%;background:transparent;overflow:hidden;
  font:500 6.2vh/1.3 -apple-system,'Segoe UI Emoji',system-ui,sans-serif;
  -webkit-user-select:none;user-select:none;color:#fff}
#stage{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;
  justify-content:flex-end;padding-bottom:4.8vh;box-sizing:border-box}
/* Reserved in flow rather than absolute, so turning the dots on never shifts the face. */
#dots{display:flex;gap:3.3vh;opacity:0;margin-bottom:6.7vh}
#dots i{width:2.9vh;height:2.9vh;border-radius:50%;background:var(--accent);
  animation:blink var(--blink) ease-in-out infinite}
#dots i:nth-child(2){animation-delay:.13s} #dots i:nth-child(3){animation-delay:.26s}
.busy #dots{opacity:1}
#figure{position:relative;animation:float var(--bob) ease-in-out infinite}
#sparkle{position:absolute;top:-1vh;right:-15vh;font-size:12vh}
#face{font-size:37vh;line-height:1}
#shadow{width:28vw;height:4.3vh;border-radius:50%;background:rgba(0,0,0,.22);margin:3.8vh 0 7.6vh}
#pill{width:76%;box-sizing:border-box;padding:4.3vh 4vh;border-radius:9vh;text-align:center;
  background:rgba(26,26,26,.91);border:1px solid color-mix(in srgb, var(--accent) 30%, transparent)}
/* Never wrap: a second line would change the pill height and shove the face upward. */
#caption,#source{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#caption{font-size:6.2vh} #source{font-size:4.8vh;font-weight:600;color:var(--accent);margin-top:1.4vh}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-3.3vh)}}
@keyframes blink{0%,100%{opacity:.25}50%{opacity:1}}
@keyframes hop{0%,100%{transform:translateY(0)}35%{transform:translateY(-10vh)}}
@keyframes wobble{0%,100%{transform:rotate(0)}25%{transform:rotate(-9deg)}75%{transform:rotate(9deg)}}
@keyframes doze{0%,100%{transform:translateY(0) rotate(-6deg)}50%{transform:translateY(-1.4vh) rotate(-6deg)}}
.s-success #figure{animation:hop var(--hop) ease-in-out infinite}
.s-error   #figure{animation:wobble var(--wobble) ease-in-out 4}
.s-sleep   #figure{animation:doze var(--doze) ease-in-out infinite}
.reduced #figure,.reduced #dots i{animation:none}
"""

JS = r"""
const POSES = __POSES__, CATS = __CATS__, ORDER = __ORDER__;
const BUSY = ['thinking','working','tool'];
// Claude reads warm, everything else reads teal — the same split the AppKit view used.
const ACCENT = { Claude: '#EB9E6E' }, DEFAULT_ACCENT = '#7ACCAE';
let view = { state:'idle', provider:'Codex', source:'', appearance:'emoji', gentle:false };
let petUntil = 0;

function render(){
  const pose = POSES[view.state] || POSES.idle;
  const petting = Date.now() < petUntil;
  document.documentElement.style.setProperty('--accent', ACCENT[view.provider] || DEFAULT_ACCENT);
  document.getElementById('face').textContent =
    view.appearance === 'cat' ? (CATS[view.state] || pose[0]) : pose[0];
  document.getElementById('caption').textContent = petting ? "You've got this \u2661" : pose[1];
  document.getElementById('sparkle').textContent = petting ? '\uD83D\uDC96' : pose[2];
  document.getElementById('source').textContent = view.provider + ' \u00b7 ' + view.source;
  const reduced = view.gentle || matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.body.className = 's-' + view.state
    + (BUSY.includes(view.state) ? ' busy' : '') + (reduced ? ' reduced' : '');
}

const tauri = window.__TAURI__;
if (tauri) {
  tauri.event.listen('update', e => { view = Object.assign(view, e.payload); render(); });
  // Right-click is handled natively so the menu matches the macOS one exactly.
  addEventListener('contextmenu', e => { e.preventDefault(); tauri.core.invoke('show_menu'); });
  // Below the threshold it is a click and you get a heart; past it, the window moves.
  let press = null;
  addEventListener('mousedown', e => { press = { x: e.screenX, y: e.screenY }; });
  addEventListener('mousemove', e => {
    if (press && Math.hypot(e.screenX - press.x, e.screenY - press.y) > 4) {
      press = null;
      tauri.core.invoke('start_drag');
    }
  });
  addEventListener('mouseup', () => {
    if (press) { petUntil = Date.now() + 2000; render(); setTimeout(render, 2100); }
    press = null;
  });
  tauri.core.invoke('ready');
} else {
  // Opened in a plain browser: cycle so the renderer can be checked without the shell.
  view.source = 'Demo';
  let i = 0;
  setInterval(() => { view.state = ORDER[i++ % ORDER.length]; render(); }, 1700);
}
render();
"""

import json
JS = (JS.replace('__POSES__', json.dumps(POSES, ensure_ascii=False))
        .replace('__CATS__', json.dumps(CATS, ensure_ascii=False))
        .replace('__ORDER__', json.dumps(ORDER, ensure_ascii=False)))

html = f"""<!doctype html><meta charset="utf-8"><title>Actor</title>
<style>{CSS}</style>
<div id="stage">
  <div id="dots"><i></i><i></i><i></i></div>
  <div id="figure"><div id="face"></div><div id="sparkle"></div></div>
  <div id="shadow"></div>
  <div id="pill"><div id="caption"></div><div id="source"></div></div>
</div>
<script>{JS}</script>
"""
out = root / 'proto/tauri/ui/index.html'
out.write_text(html)
print(f'wrote {out} — {len(POSES)} moods, {len(CATS)} cat moods, {len(html)} bytes')
