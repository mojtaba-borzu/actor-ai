# Desktop AI coding companion — design system

An original anime-inspired swordsman who lives on the desktop and shows what an AI coding
agent is doing, without text.

Read in order:

| File | What it settles |
|---|---|
| [00-decisions.md](00-decisions.md) | What is locked, what is still open, what was rejected from the original brief and why |
| [01-character-canon.md](01-character-canon.md) | Proportions, face, value ladder, costume, emblem, sword, FX, camera, anchor, motion character |
| [02-state-system.md](02-state-system.md) | 12 pose families, the real agent events behind them, timing and concurrency policy |
| [03-production-pipeline.md](03-production-pipeline.md) | Layer manifest, sheets, generation protocol, runtime, licensing, v1 plan |
| [prompts/01-canon-frame.md](prompts/01-canon-frame.md) | The locked generation prompts |

Assets:

| File | What it is |
|---|---|
| `assets/master/hero-3q.svg` | The 3/4 hero master, layered to the manifest, on canon geometry |
| `assets/master/sword.svg` | Sheet D — one sword geometry, six energy states |
| `assets/master/fx-kit.svg` | FX primitives, in character master space |
| `tools/build-assets.py` | Builds the sword sheet, the FX kit and the state viewer from one geometry source |
| `tools/legibility-test.html` | The contrast gate: 120/180/256 px over light, dark and colour backgrounds |
| `tools/state-viewer.html` | Six composed states, to check FX readability at size |

Sword and FX geometry is defined once, in `tools/build-assets.py`. Edit it there and rebuild —
never hand-edit the generated sheets, or the geometry will drift between files.

Nothing is drawn, generated or rigged against a decision still marked `OPEN` in
[00-decisions.md](00-decisions.md).
