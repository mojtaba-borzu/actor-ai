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
html,body{margin:0;height:100%;background:transparent;overflow:hidden;
  font:500 13px/1.3 -apple-system,'Segoe UI Emoji',system-ui,sans-serif;
  -webkit-user-select:none;user-select:none;-webkit-app-region:drag;color:#fff}
#stage{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;
  justify-content:flex-end;padding-bottom:10px;box-sizing:border-box}
/* Reserved in flow rather than absolute, so turning the dots on never shifts the face. */
#dots{display:flex;gap:7px;opacity:0;margin-bottom:14px}
#dots i{width:6px;height:6px;border-radius:50%;background:#7ACCAE;animation:blink 1.2s ease-in-out infinite}
#dots i:nth-child(2){animation-delay:.18s} #dots i:nth-child(3){animation-delay:.36s}
.busy #dots{opacity:1}
#figure{position:relative;animation:float 2.6s ease-in-out infinite}
#sparkle{position:absolute;top:-2px;right:-32px;font-size:25px}
#face{font-size:78px;line-height:1}
#shadow{width:70px;height:9px;border-radius:50%;background:rgba(0,0,0,.22);margin:8px 0 16px}
#pill{width:92%;box-sizing:border-box;padding:9px 12px;border-radius:19px;text-align:center;
  background:rgba(26,26,26,.91);border:1px solid rgba(122,204,174,.3)}
#caption{font-size:13px} #source{font-size:10px;font-weight:600;color:#7ACCAE;margin-top:3px}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-7px)}}
@keyframes blink{0%,100%{opacity:.25}50%{opacity:1}}
@keyframes hop{0%,100%{transform:translateY(0)}35%{transform:translateY(-22px)}}
@keyframes wobble{0%,100%{transform:rotate(0)}25%{transform:rotate(-9deg)}75%{transform:rotate(9deg)}}
@keyframes doze{0%,100%{transform:translateY(0) rotate(-6deg)}50%{transform:translateY(-3px) rotate(-6deg)}}
.s-success #figure{animation:hop .6s ease-in-out infinite}
.s-error   #figure{animation:wobble .45s ease-in-out 3}
.s-sleep   #figure{animation:doze 5s ease-in-out infinite}
.reduced #figure,.reduced #dots i{animation:none}
"""

JS = """
const POSES = __POSES__, CATS = __CATS__, ORDER = __ORDER__;
const BUSY = ['thinking','working','tool'];
// Storage can throw in a private or sandboxed context; the palette is a
// convenience, never a reason for the renderer to fail to draw.
const store = {
  get(k){ try { return localStorage.getItem(k) } catch (e) { return null } },
  set(k, v){ try { localStorage.setItem(k, v) } catch (e) {} }
};
let skin = store.get('skin') || 'emoji';
let current = 'idle';

function render(){
  const pose = POSES[current] || POSES.idle;
  document.getElementById('face').textContent = skin === 'cat' ? (CATS[current] || pose[0]) : pose[0];
  document.getElementById('caption').textContent = pose[1];
  document.getElementById('sparkle').textContent = pose[2];
  document.body.className = 's-' + current + (BUSY.includes(current) ? ' busy' : '')
    + (matchMedia('(prefers-reduced-motion: reduce)').matches ? ' reduced' : '');
}
function show(state){ current = POSES[state] ? state : 'idle'; render(); }
function setSource(text){ document.getElementById('source').textContent = text; }

// Click cycles the palette, matching the Appearance menu on macOS.
addEventListener('click', () => {
  skin = skin === 'emoji' ? 'cat' : 'emoji';
  store.set('skin', skin); render();
});

show('idle');
const tauri = window.__TAURI__;
if (tauri && tauri.event) {
  setSource('Codex \\u00b7 Live');
  tauri.event.listen('state', e => show(e.payload));
} else {
  setSource('Demo');
  let i = 0;
  setInterval(() => show(ORDER[i++ % ORDER.length]), 1700);
}
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
