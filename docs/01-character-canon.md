# Character canon

The single source of truth for the character's shape, colour and proportion.
If a generated image, a redraw or a rig disagrees with this file, this file wins.

All measurements are in **H** = one head height. Body height = **6.5 H** (D4).
Pixel figures in brackets are at the reference render size of **180 device px character height**, where 1 H ≈ 27.7 px.

---

## 1. Identity

Male, reads 24–27. Calm, observant, disciplined, quietly playful. Competent rather than heroic.

The emotional contract: he is a **coworker at the next desk**, not a performer. A user has him in peripheral vision for eight hours. Every motion decision is judged against "would this still be tolerable on hour six?" — which rules out startle reactions, bouncing, and anything that pulls the eye when nothing has changed.

## 2. Proportion table

Measured from the top of the skull, in H.

| Landmark | Position | Landmark | Position |
|---|---|---|---|
| Chin | 1.00 H | Hip / crotch | 3.10 H |
| Shoulder line | 1.35 H | Wrist (arm at rest) | 3.30 H |
| Chest | 1.80 H | Fingertips | 3.75 H |
| Elbow / waist | 2.50 H | Knee | 4.70 H |
| | | Ankle | 6.25 H |
| | | Sole (ground line) | 6.50 H |

| Width | Value | | Width | Value |
|---|---|---|---|---|
| Head | 0.78 H | | Waist | 1.05 H |
| Shoulders | 1.85 H [51 px] | | Hips | 1.25 H |

Hand length **0.85 H** [23 px]. Hands are drawn one step larger than strict anatomy — they carry gesture at small sizes and are the second-most-read element after the head silhouette.

Foot length **0.95 H**. Feet stay visibly separated in every standing pose; merged feet destroy the standing silhouette below 150 px.

## 3. Face

Within the head, measured from the top of the skull:

| Feature | Position | Size |
|---|---|---|
| Eyeline (eye centre) | 0.58 H | eye 0.17 H tall [4.7 px] × 0.26 H wide [7.2 px] |
| Inter-eye gap | — | 0.25 H |
| Eyebrow (resting, lower edge) | 0.46 H | thickness 0.06 H [1.7 px, floor 2 device px] |
| Nose | 0.74 H | a single shadow mark, no outline |
| Mouth | 0.86 H | width 0.20 H at rest |
| Ear top | 0.55 H | — |

**Eyebrows are the primary expression channel.** Their vertical travel range must be at least **0.12 H** [3.3 px] between the lowest (focused) and highest (surprised) position, and each brow must be able to move independently. If a brow shape cannot travel 3 device px at the minimum render size, the expression does not exist.

Face shape: slightly angular, soft jawline, defined enough to read as an adult, never rounded-babyface. Eyes are alert and medium-large — sharp enough to read as intelligent, not so large that they read as a teenager.

**Cut from the brief:** the "subtle cyan reflection in the pupil". At 180 px the pupil is ~2 px. The AI-active eye signal is instead carried by a **1 px cyan lower-lid line** across the eye opening, which survives downscaling.

## 4. Value ladder (the single most important fix)

The original palette spans only **0.8 % to 2.1 % relative luminance** (about 8.7 L\* points) and the hair value falls inside that same band. Rendered on a transparent window over a dark IDE, that is a silhouette that does not exist, with the head dissolved into the torso.

The canon therefore defines an explicit value ladder. Brief colours are kept; the missing steps are added.

| Step | Hex | Role |
|---|---|---|
| K0 | `#080B10` | Contour line. 2 device px at 180, scales with render size, never below 1.5 px. |
| K1 | `#11161D` | Jacket core shadow *(from brief)* |
| K2 | `#1B222C` | Jacket base *(brief's #171D26 / #202832 collapsed to one usable base)* |
| K3 | `#2A3441` | Jacket top plane — shoulders, upper sleeve, thigh top |
| K4 | `#3E4B5C` | Panel edges, seam highlights, sole edge |
| K5 | `#6C7788` | **Inner shirt.** Added, and load-bearing — see below. |
| K6 | `#9AA5B5` | Shirt highlight, collar edge |
| K7 | `#E6EDF4` @ 30 % | Outer halo, 1 px outside the contour |

**The head/torso break is carried by the K5 collar, not by hair-vs-jacket value.** The inner shirt is changed from the brief's "simple dark inner shirt" to a mid-light grey, visible as a collar band and a narrow chest V. This is what stops the head merging into the shoulders below 200 px. It is not decorative and must not be darkened for aesthetic reasons.

**Dual-edge legibility rule.** Every silhouette carries both a K0 contour *and* a K7 halo one pixel outside it. The contour carries the character on light wallpapers; the halo carries it on dark ones. Together they mean the character never needs to know what is behind the window.

This supersedes the brief's "soft neutral studio lighting, no rim light" rule, which is incompatible with a transparent window over arbitrary backgrounds.

### Hair

| Step | Hex | Role |
|---|---|---|
| — | `#1A1613` | Core shadow *(brief #191614)* |
| — | `#2A2320` | Base mass *(brief #29211E)* |
| — | `#46392F` | Top plane — the lit upper mass |
| — | `#4FD6D0` @ 40 % | Cyan rim along the upper-left silhouette when AI energy is active |

Hair is built from **5 masses, not strands**: back mass, upper crown plane, a heavy front-left forelock, a lighter front-right sweep, and one short spike at the crown-right that breaks the outline. That last spike is the single most recognisable point of the silhouette and must survive every pose. No loose flyaway strands — they turn to noise below 200 px and are expensive to rig.

### Skin

`#F2D6C0` base · `#D9AE96` shadow · `#B98974` deep shadow · `#7A4E3F` skin contour (never K0 — a black outline on skin reads as ink at small size).

### Energy palette

| Role | Hex | FX shape (see §7) |
|---|---|---|
| AI core | `#27D9D0` | — |
| Energy highlight core | `#B8FFFA` | the 1 px bright centre inside any glow |
| Secondary / data | `#3FA9F5` | — |
| Success | `#56D89A` | expanding ring |
| Warning | `#FFB547` | stacked chevrons |
| Error | `#FF675D` | broken shard |

**Colour is never the only state channel.** `#27D9D0` and `#56D89A` are hard to separate under deuteranopia, and `#FFB547` vs `#FF675D` under protanopia. Every state that signals by colour also signals by FX *shape* and by *rhythm* (a ring expands once; chevrons pulse twice; a shard breaks and reassembles).

## 5. Costume

Modern techwear, contemporary, never historical. Built from large flat panels so that it rigs cheaply and reads at size.

- **Jacket** — short, ends at the hip bone, never below. Asymmetric front closure offset to the left of centre. Exactly **4 panels per side** (chest, waist, upper sleeve, forearm sleeve). Standing collar, low enough to leave the neck and jaw readable. No hood — a hood destroys the head silhouette and adds a deforming mass behind the neck.
- **Inner shirt** — K5/K6, visible at the collar and in a narrow chest V. Load-bearing (§4).
- **Trousers** — K2 base, K3 top plane, fitted, with one horizontal seam break at mid-thigh to give the knee joint a landmark.
- **Boots** — low, K1 with a K4 sole edge. The sole edge is the only thing that separates the feet from a dark background, so it is always present.
- **Forearm bands** — one thin K4 band on each forearm, which doubles as the wrist joint landmark for rigging.

Banned, and the ban is structural rather than stylistic: capes, scarves, long coats, hoods, chains, multiple straps, harnesses, any pattern smaller than 0.1 H, anything that crosses a joint.

Joints stay visible: shoulder, elbow, wrist, hip, knee and ankle each have a value change or a seam within 0.15 H of the joint centre.

## 6. Emblem

One emblem, worn small on the left chest panel, and repeated at 3× size on the jacket back.

**"The aperture cut"** — a rounded square outline with the top-right corner notched open; a single straight stroke crosses it diagonally at 45°, offset below centre, and overshoots the outline slightly on both ends; the stroke terminates at its upper end in a small solid square block, like a cursor.

Reads as: a block, cut open, leaving a caret. Structurally: three primitives, no curves other than corner radii, no text, no glyph, no infinity form, no vendor mark.

- Must resolve at **8 device px**: at that size only the square, the notch and the diagonal survive, and that is the intended reading.
- Skinnable by recolouring the stroke only; the square stays K4.
- **Requires a trademark clearance search before the repo is public** (D6, D9). Abstract geometric marks collide more often than they look like they should.

## 7. Energy / FX system

Five ordered FX slots, never more:

| Slot | Draw order | Contents |
|---|---|---|
| `fx_ground` | behind everything | contact pool, dissolve pool |
| `fx_back` | behind character | orbiting fragments, portals, holographic panels |
| `fx_blade` | with the blade | edge glow, charge travel, impact flash |
| `fx_front` | in front of character | head particles, foreground sparks |
| `fx_rim` | topmost | the cyan silhouette rim |

**FX budget.** FX may never occupy more than 25 % of the character's bounding box, and never more than two slots simultaneously below 200 px.

**LOD tiers**, switched on render size:

| Size | Active slots | Minimum particle size | Minimum line weight |
|---|---|---|---|
| ≥ 256 px | all five | 2 px | 1.5 px |
| 180–255 px | blade, front, rim | 3 px | 2 px |
| < 180 px | blade + one other | 4 px | 2.5 px |

Anything thinner than the minimum line weight is removed, not scaled. A 1 px cyan line at 120 px shimmers on every sub-pixel move and reads as dirt on the screen.

**Additive blending is not available.** A transparent always-on-top window composites against unknown content, and per-pixel alpha behaviour is inconsistent across macOS, Windows and Linux/Wayland. All glow is authored as **explicit soft-edged shapes with a bright `#B8FFFA` core**, not as an additive pass. This must be confirmed on all three platforms before the FX kit is authored — if any target lacks per-pixel alpha, the FX language changes to hard-edged opaque shapes, which changes the art, not just the code.

## 8. Sword

No sheath (D2). The blade assembles from cyan fragments over 6–8 frames when an execution state begins, and disassembles the same way when it ends. It is absent from roughly 25 of the 40 states, which is also why its length cannot drift.

| Part | Length | Notes |
|---|---|---|
| Total | 2.60 H [72 px] | fixed, never scales with pose |
| Blade | 1.90 H | straight, no curvature, slight distal taper, asymmetric chisel tip |
| Guard | 0.15 H | a small rectangular bracket, not a disc or oval |
| Grip | 0.55 H | smooth dark cylinder, one geometric notch, no wrap, no braid |

Blade width 0.13 H [3.6 px], with a **floor of 3 device px** total including the glow core — below that the sword disappears whenever it crosses the torso.

The straight blade, bracket guard and unwrapped grip are deliberate: curvature, a disc guard and a wrapped hilt are the three cues that make a sword read as a specific traditional weapon, and removing all three is the cheapest distance to put between this design and the franchises on the negative list.

Energy states: **inactive** (not present) · **forming** (fragments, 6–8 frames) · **working** (soft `#27D9D0` edge) · **execution** (strong `#27D9D0` → `#B8FFFA` core, one travelling pulse) · **error** (`#FF675D` break in the edge line, ≤ 0.4 s) · **success** (one `#56D89A` ring from the tip).

## 9. Camera, canvas and anchor

- **One virtual camera** for every state: 3/4 left, chest height, long lens, effectively no perspective convergence. Side and back views are separate authored views, not camera moves.
- **Master art** is authored at **512 px character height** on a **768 × 768** canvas.
- **Ground anchor is fixed at (384, 700)** in master space and is identical in every state. The anchor, not the bounding box, is what the window positions against — this is what stops the character jittering when the state changes.
- **Sword safe area**: 60 px above the crown and 120 px to each side stay free of the canvas edge, so execution poses never clip.
- Exports are defined by **character height in device pixels** — 128 / 192 / 256 / 384 — not by canvas size. A vector runtime makes these free and avoids the non-integer downscale shimmer that a raster sheet would produce.
- Minimum supported render is **120 device pixels of character height**, measured on a 1× display. Windows laptops at 100 % scaling are common in this audience and are the worst case that must be tested.

## 10. Motion character

| State | Motion signature |
|---|---|
| Idle | 4–6 s breath, weight shift every third cycle, blink on a randomised 3–7 s interval that is never part of a baked loop |
| Thinking | small, still, upward eye drift; the body barely moves |
| Working | precise, economical, no wasted travel |
| Debugging | slow and deliberate, the only state that crouches |
| Error | a half-beat pause, then a small controlled recovery — **never a startle** |
| Retry | one breath, eyes sharpen, no flourish |
| Success | a single nod and a small smile; the FX carries the celebration, not the body |
| Sleep | 5 s breath, no Z glyphs, no exaggeration |

**The error rule is a hard rule.** Errors fire many times in a normal session. Any animation containing surprise, recoil or frustration becomes an irritant by the third repeat and a reason to uninstall by the tenth. Error reads as *noticing*, not as *reacting*.

**Three power tiers**, because an always-on-top transparent window repainting continuously for eight hours is the most likely cause of a day-two uninstall:

| Tier | When | Frame rate |
|---|---|---|
| Active | a state is playing | 30–60 fps |
| Ambient | idle, user present | 10–12 fps |
| Dormant | idle, no events for N minutes | static frame, zero repaint |

The dormant frame and the first frame of the ambient loop must be the same drawing apart from the breath offset, or entering dormant will visibly pop.
