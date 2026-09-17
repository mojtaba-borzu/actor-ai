#!/usr/bin/env python3
"""Builds the sword sheet, the FX kit and the state viewer from one geometry source.
Sword and FX geometry is defined ONCE here so it cannot drift between files."""
import base64, pathlib

CY, CORE, BLUE, OK, WARN, ERR = "#27D9D0", "#B8FFFA", "#3FA9F5", "#56D89A", "#FFB547", "#FF675D"

# --- sword -------------------------------------------------------------------
# Local space, origin at the grip point where the hand closes.
# Canon: total 2.60 H = 205, blade 1.90 H = 150, guard 0.15 H = 12, grip 0.55 H = 43,
# blade width 0.13 H = 10.2. Tip at y=-184, pommel at y=+21. Geometry never varies by state.
BLADE = 'M-5.1 -34 L-4.3 -158 L4.3 -184 L5.1 -34 Z'
BEVEL = 'M-5.1 -34 L-4.3 -158 L-0.6 -160 L-1.4 -34 Z'
EDGE  = 'M4.3 -184 L5.1 -34'
CHIS  = 'M-4.3 -158 L4.3 -184'
HILT  = ('<path d="M-11 -34 L11 -34 L11 -21 L6 -21 L6 -27 L-6 -27 L-6 -21 L-11 -21 Z" fill="#2A3441" stroke="#080B10" stroke-width="3" stroke-linejoin="round"/>'
         '<rect x="-4.2" y="-21" width="8.4" height="36" rx="2" fill="#1B222C" stroke="#080B10" stroke-width="3"/>'
         '<rect x="-4.2" y="-6" width="8.4" height="5" fill="#3E4B5C"/>'
         '<rect x="-5.5" y="15" width="11" height="6" rx="1.5" fill="#2A3441" stroke="#080B10" stroke-width="2.4"/>')

def sword(state="working"):
    """state: inactive | forming | working | execution | error | success"""
    if state == "inactive":
        return f'<g class="sword">{HILT}</g>'
    op = 0.45 if state == "forming" else 1
    o  = [f'<g class="sword" opacity="{op}">']
    if state == "execution":
        o.append(f'<path d="{BLADE}" fill="none" stroke="{CY}" stroke-width="16" stroke-linejoin="round" opacity=".28"/>')
    o.append(f'<path d="{BLADE}" fill="#232A34" stroke="#080B10" stroke-width="3" stroke-linejoin="round"/>')
    o.append(f'<path d="{BEVEL}" fill="#3E4B5C" opacity=".75"/>')
    if state in ("working", "success"):
        o.append(f'<path d="{EDGE}" stroke="{CY}" stroke-width="2.6" fill="none" stroke-linecap="round"/>')
        o.append(f'<path d="{CHIS}" stroke="{CY}" stroke-width="2.2" fill="none" stroke-linecap="round"/>')
    if state == "execution":
        o.append(f'<path d="{EDGE}" stroke="{CY}" stroke-width="5" fill="none" stroke-linecap="round"/>')
        o.append(f'<path d="{EDGE}" stroke="{CORE}" stroke-width="1.8" fill="none" stroke-linecap="round"/>')
        o.append(f'<path d="{CHIS}" stroke="{CORE}" stroke-width="2.4" fill="none" stroke-linecap="round"/>')
        o.append(f'<path d="M4.6 -150 L5.0 -96" stroke="{CORE}" stroke-width="7" stroke-linecap="round" opacity=".9"/>')
    if state == "error":
        o.append(f'<path d="M4.3 -184 L4.8 -118" stroke="{CY}" stroke-width="2.6" fill="none" stroke-linecap="round"/>')
        o.append(f'<path d="M5.0 -86 L5.1 -34" stroke="{CY}" stroke-width="2.6" fill="none" stroke-linecap="round"/>')
        o.append(f'<path d="M4.8 -118 L14 -108 L2 -100 L12 -92 L5.0 -86" stroke="{ERR}" stroke-width="3" fill="none" stroke-linejoin="round"/>')
    if state == "forming":
        for i, (dx, dy) in enumerate([(13,-160),(-14,-128),(15,-92),(-13,-62),(12,-44)]):
            o.append(f'<rect x="{dx-4}" y="{dy-4}" width="8" height="8" fill="{CY}" opacity="{0.8-i*0.1:.2f}" transform="rotate(45 {dx} {dy})"/>')
    o.append(HILT)
    if state == "success":
        o.append(f'<circle cx="0" cy="-184" r="34" fill="none" stroke="{OK}" stroke-width="4.5" opacity=".85"/>')
        o.append(f'<circle cx="0" cy="-184" r="52" fill="none" stroke="{OK}" stroke-width="2.4" opacity=".4"/>')
    o.append('</g>')
    return ''.join(o)

# --- FX kit ------------------------------------------------------------------
# Minimum particle 3 device px at 180 => 8.5 master units. Nothing smaller ships.
def diamond(x, y, s, c, op=1):
    return f'<rect x="{x-s/2}" y="{y-s/2}" width="{s}" height="{s}" fill="{c}" opacity="{op}" transform="rotate(45 {x} {y})"/>'

def fx_think(ox=0, oy=0):
    return (f'<g id="fx_think" transform="translate({ox},{oy})">'
            + diamond(430, 196, 10, CY, .95) + diamond(452, 168, 8.5, CY, .7)
            + diamond(414, 156, 9, BLUE, .55) + '</g>')

def fx_portal(cx=470, cy=440):
    return (f'<g id="fx_portal">'
            f'<circle cx="{cx}" cy="{cy}" r="44" fill="none" stroke="{CY}" stroke-width="5" '
            f'stroke-dasharray="52 22" opacity=".9"/>'
            f'<circle cx="{cx}" cy="{cy}" r="27" fill="none" stroke="{CORE}" stroke-width="3" '
            f'stroke-dasharray="26 16" opacity=".8"/>'
            f'<circle cx="{cx}" cy="{cy}" r="9" fill="{CY}" opacity=".9"/></g>')

def fx_command():
    return (f'<g id="fx_command"><path d="M250 566 L540 566" stroke="{CY}" stroke-width="5" '
            f'stroke-linecap="round" opacity=".95"/>'
            f'<path d="M300 566 L480 566" stroke="{CORE}" stroke-width="2" stroke-linecap="round"/>'
            + diamond(556, 560, 9, CY, .8) + diamond(578, 574, 8.5, CY, .5)
            + diamond(232, 572, 8.5, CY, .6) + '</g>')

def fx_ring(cx=384, cy=430, c=OK):
    return (f'<g id="fx_ring"><circle cx="{cx}" cy="{cy}" r="96" fill="none" stroke="{c}" '
            f'stroke-width="5" opacity=".75"/><circle cx="{cx}" cy="{cy}" r="128" fill="none" '
            f'stroke="{c}" stroke-width="2.6" opacity=".35"/></g>')

def fx_shard(cx=470, cy=470):
    return (f'<g id="fx_shard"><path d="M{cx-26} {cy-18} L{cx-4} {cy-30} L{cx+6} {cy-6} '
            f'L{cx+28} {cy+4} L{cx+2} {cy+14} L{cx-10} {cy+34} L{cx-16} {cy+6} Z" '
            f'fill="none" stroke="{ERR}" stroke-width="4" stroke-linejoin="round" opacity=".95"/>'
            + diamond(cx+40, cy-26, 9, ERR, .7) + diamond(cx-40, cy+30, 8.5, ERR, .5) + '</g>')

def fx_chevrons(cx=470, cy=430):
    p = ''.join(f'<path d="M{cx-22} {cy+i*22} L{cx} {cy-14+i*22} L{cx+22} {cy+i*22}" fill="none" '
                f'stroke="{WARN}" stroke-width="5" stroke-linejoin="round" stroke-linecap="round" '
                f'opacity="{0.95-i*0.25}"/>' for i in range(3))
    return f'<g id="fx_chevrons">{p}</g>'

def fx_orbit():
    pts = [(300,330),(468,300),(492,436),(286,452)]
    return ('<g id="fx_orbit"><ellipse cx="384" cy="380" rx="112" ry="82" fill="none" '
            f'stroke="{CY}" stroke-width="2.2" opacity=".28"/>'
            + ''.join(diamond(x, y, 10, CY, .8) for x, y in pts) + '</g>')

def fx_panel():
    lines = ''.join(f'<path d="M{486+ (i%3)*8} {330+i*22} L{486+(i%3)*8+(96-(i%4)*22)} {330+i*22}" '
                    f'stroke="{CY}" stroke-width="4" stroke-linecap="round" opacity=".55"/>' for i in range(6))
    return ('<g id="fx_panel"><path d="M474 306 L616 296 L616 476 L474 466 Z" fill="'+CY+'" '
            'opacity=".09" stroke="'+CY+'" stroke-width="2.6"/>' + lines + '</g>')

def fx_assemble():
    pts = [(330,250),(444,300),(300,430),(470,520),(360,600),(430,180),(280,540)]
    return ('<g id="fx_assemble">' + ''.join(diamond(x, y, 11, CY, .75) for x, y in pts) + '</g>')

def fx_shadow():
    return ('<g id="fx_shadow"><ellipse cx="384" cy="702" rx="78" ry="11" fill="#080B10" opacity=".22"/>'
            '<ellipse cx="384" cy="702" rx="46" ry="7" fill="#080B10" opacity=".18"/></g>')

# --- writers -----------------------------------------------------------------
root = pathlib.Path(__file__).resolve().parent.parent
STATES = ["inactive", "forming", "working", "execution", "error", "success"]

sheet = ''.join(f'<g transform="translate({80+i*88},236)">{sword(s)}</g>' for i, s in enumerate(STATES))
(root/'assets/master/sword.svg').write_text(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 588 300" width="588" height="300" '
    'role="img" aria-label="Sword sheet, six energy states">\n'
    '<!-- Sheet D. Geometry is identical in all six states; only the energy layer changes. -->\n'
    f'{sheet}\n</svg>\n')

kit = [fx_shadow(), fx_think(), fx_portal(), fx_command(), fx_ring(), fx_shard(),
       fx_chevrons(), fx_orbit(), fx_panel(), fx_assemble()]
(root/'assets/master/fx-kit.svg').write_text(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 768 768" width="768" height="768" '
    'role="img" aria-label="FX kit primitives">\n'
    '<!-- Every primitive in character master space so it drops straight into an FX slot. -->\n'
    + '\n'.join(kit) + '\n</svg>\n')

# --- composed states ---------------------------------------------------------
hero = (root/'assets/master/hero-3q.svg').read_text()
HAND = 'translate(340,452) rotate(198)'

def compose(ground='', back='', sword_state=None, blade='', front=''):
    s = hero
    s = s.replace('<g id="fx_ground"></g>', f'<g id="fx_ground">{ground}</g>')
    s = s.replace('<g id="fx_back"></g>', f'<g id="fx_back">{back}</g>')
    if sword_state:
        s = s.replace('<g id="sword_slot"></g>',
                      f'<g id="sword_slot" transform="{HAND}">{sword(sword_state)}</g>')
    s = s.replace('<g id="fx_blade"></g>', f'<g id="fx_blade">{blade}</g>')
    s = s.replace('<g id="fx_front"></g>', f'<g id="fx_front">{front}</g>')
    return s

SCENES = [
    ("idle",       compose(ground=fx_shadow())),
    ("thinking",   compose(ground=fx_shadow(), front=fx_think())),
    ("working",    compose(ground=fx_shadow(), back=fx_panel(), sword_state="working")),
    ("tool call",  compose(ground=fx_shadow(), back=fx_portal(), sword_state="execution")),
    ("error",      compose(ground=fx_shadow(), sword_state="error", front=fx_shard())),
    ("success",    compose(ground=fx_shadow(), back=fx_ring(), sword_state="working")),
]

def uri(svg): return 'data:image/svg+xml;base64,' + base64.b64encode(svg.encode()).decode()
def cells(h): return ''.join(f'<div class="c"><img src="{uri(s)}" height="{h}"><b>{n}</b></div>'
                             for n, s in SCENES)
html = ('<!doctype html><meta charset="utf-8"><title>States</title><style>'
        'body{margin:0;font:12px/1.4 -apple-system,system-ui,sans-serif}'
        '.p{padding:10px 14px}.r{display:flex;align-items:flex-end;gap:6px;flex-wrap:wrap}'
        '.c{text-align:center}.c b{display:block;font-weight:600;opacity:.75;margin-top:2px;font-size:10px}'
        'h3{margin:0 0 6px;font-size:10px;letter-spacing:.09em;text-transform:uppercase;opacity:.55}'
        '.light{background:#F5F5F7;color:#444}.dark{background:#10131A;color:#8a94a3}'
        'img{display:block}</style>'
        f'<div class="p dark"><h3>dark IDE &middot; 256 px</h3><div class="r">{cells(384)}</div></div>'
        f'<div class="p light"><h3>light wallpaper &middot; 180 px</h3><div class="r">{cells(270)}</div></div>'
        f'<div class="p dark"><h3>dark IDE &middot; 120 px</h3><div class="r">{cells(180)}</div></div>')
(root/'tools/state-viewer.html').write_text(html)
print("built: sword.svg, fx-kit.svg, state-viewer.html")
