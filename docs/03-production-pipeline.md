# Production pipeline

## 1. Where AI generation sits

AI image generation is used for **design exploration and reference only** (D1). It does not produce shipped assets.

The reason is mechanical, not ideological. The shipped asset must be a layered, riggable master with a fixed anchor, a fixed sword length and an 8-px-legible emblem. A raster generator emits a flat image and re-derives every detail on every call. Drift shows up first and worst in exactly the places that carry identity: the emblem, blade length, shoe shape, hair part, jacket seams and eye spacing. Asking a model for 40 consistent poses is fighting the tool; asking it for one good design and then rigging that design is using it.

There is a second reason. Raw model output is very likely uncopyrightable in the US, so the only assets the project can meaningfully own are ones with substantial human authorship — which the redraw step creates.

Pipeline:

```
concept exploration (AI)  →  locked canon frame (AI)  →  reference sheets (AI)
        →  human vector redraw: the master  →  Rive rig  →  state machine  →  app
```

## 2. Layer manifest (hero 3/4 view)

The brief's "~30 layers" is a rig-node list, not an art list. The honest count for one view:

| Group | Drawables | Contents |
|---|---|---|
| Head | ~30 | 5 hair masses, 2 ears, face base, jaw shadow, nose mark, blush, 7 parts per eye × 2, 2 brows, mouth |
| Body | 10 | neck, neck shadow, collar, shirt V, 2 jacket front panels, jacket back, hem, belt, emblem |
| Arms | 10 | per arm: deltoid cap, upper sleeve, forearm sleeve, wrist band, hand |
| Legs | 14 | per leg: hip, thigh, knee, shin, ankle, boot upper, boot sole |
| Sword | 6 | blade, edge, glow core, guard, grip, pommel — no sheath (D2) |
| FX | 5 | the five slots from the canon |
| Support | 2 | contact shadow, halo |
| **Base total** | **~77** | |

Plus swap sets, which is where the brief's count really breaks: ~10 mouth shapes, ~8 lid sets per eye, ~8 brow shapes per brow, ~10 hand poses per hand. That is roughly **+60 drawables**, for about **140 pieces in the hero view alone**.

Two caveats, stated honestly: these are estimates, not measurements, and the side and back views add their own counts. The plan should be re-costed against the real number once the master exists, not before.

## 3. Sheets

Sheets are **communication artefacts**, not production assets. A labelled grid is useful for agreeing on a design and useless for shipping: production assets are single-pose, transparent, fixed-canvas and fixed-anchor, with no text anywhere in the file.

| Sheet | Purpose | When |
|---|---|---|
| A — master turnaround | front / 3-4 / side / back at identical scale | after the canon frame is locked |
| B — face | 11 expressions, same head angle and scale | with A |
| C — hands | 10 poses, the shapes the rig swaps between | with A |
| D — sword | inactive / forming / working / execution / error / success | with A |
| E — core poses | the nine v1 states | after A–D are approved |
| F — movement | walk, run, appear, disappear | v1.1, side view |
| G — desktop interaction | sit on window, dragged, notification, sleeping | v1.1 |

Sheet H from the brief (five keyframes per animation) is dropped for looping states — start / anticipation / action / follow-through / return is a one-shot structure and describes a loop incorrectly. Loops are specified by their pose extremes and their cycle length instead.

## 4. Generation protocol

1. **Explore** — four direction candidates from one prompt, 3/4 view, full body, flat background. Vary only silhouette and costume detail, never proportion.
2. **Lock the canon frame** — one single image, 3/4 view, full body, neutral pose, no FX, no sword. This image is the reference for everything after it. Nothing else is generated until it is approved.
3. **Derive sheets** — every subsequent generation passes the canon frame's `job_id` as reference media, and restates every locked detail from the canon in the prompt. Restating is not redundant; a detail that is not restated is a detail that will drift.
4. **Never** pass the old 3D reference sheet as reference media (D-rejected list).

Practical notes for whoever runs this:

- Preflight cost with `get_cost: true` before any batch. Do not pass `use_unlim` unless the user has explicitly asked to spend their free-trial generations.
- Verify the model catalogue before budgeting — `models_explore` was returning 401 during planning, so aspect ratios, native transparent-background support and reference-media roles are unconfirmed. If the general image model does support a transparent background natively, the background-removal step and its matte artefacts on the glow edge disappear.
- Background removal on a thin, semi-transparent cyan glow is the known weak point of the cutout path. Author glow separately from the character wherever possible.
- **Do not ask a generator for walk or run cycle frames.** The image models here have no temporal conditioning, so independently sampled frames boil — limb volume and shading shift every frame. Locomotion comes from the rig.
- Expect a low accept rate early. Treat any total-generations figure as a placeholder until measured on the first real sheet.

## 5. Runtime

Rive, single target (D5). The state machine maps one-to-one onto the pose families; vector makes every render size free; runtime layer tinting is what makes the skin system and the five accent colours possible without re-exporting art. Draw order in Rive is authored as keyed rules per state rather than set imperatively at runtime — the cross-body blade still works, but it has to be authored deliberately, so budget for it.

One derived artefact: a pre-rendered frame sequence generated **from** the Rive file for any surface that cannot run it.

## 6. Repo structure and licensing

```
/assets/master/        vector master, one file per view
/assets/rive/          .riv source and exports
/assets/reference/     AI exploration output, kept out of the build
/docs/                 this canon
LICENSE                code: MIT or Apache-2.0
LICENSE-ASSETS         art: CC BY 4.0
TRADEMARK.md           name + emblem reserved
AI-DISCLOSURE.md       provenance of AI-assisted assets
```

Why this split (D6): a single root `LICENSE` makes everyone downstream treat the art as MIT, which cannot be undone once forks exist. CC BY 4.0 on the art keeps the community skin system possible and keeps the project packageable by Debian and Fedora — an NC or ND licence blocks both, and F-Droid would ship it flagged with the `NonFreeAssets` anti-feature rather than refusing it. Meanwhile the copyright in raw generated art is probably unenforceable anyway, so the restriction buys little and costs features.

The protection that *does* work is trademark: there is no human-authorship requirement in trademark law, so the name and emblem are registrable if distinctive and used in commerce. `TRADEMARK.md` plus the ™ symbol costs nothing and should be in the first commit. Registration can wait for traction.

Two practical items: keep third-party AI vendor names out of the product name, icon and store listing — the app and extension stores reject them — and disclose AI-assisted assets where required. Steam's rules changed in January 2026 to a two-tier model: pre-generated AI content shipped in the build is still disclosable, while AI coding assistance is not.

## 7. v1 plan

| Step | Output | Gate |
|---|---|---|
| 1 | Canon approved | this repo |
| 2 | Four exploration candidates | one direction chosen |
| 3 | Canon frame | locked, referenced by everything after |
| 4 | Sheets A–D | design signed off |
| 5 | Vector master, hero view, ~140 pieces | matches canon measurements exactly |
| 6 | Rive rig + 9-state machine | — |
| 7 | Desktop shell + hook bridge | reads `PermissionRequest`, `PreToolUse`, `PostToolUse`, `Stop`, `SessionStart/End`, `Notification` |
| 8 | **Live gate** | a real working day with it on screen |

Step 8 is the point of the whole plan. Three things can only be answered there, and all three can invalidate art: whether the silhouette holds over a real dark IDE, whether the event rate feels alive or frantic, and whether the error state is still tolerable on its fortieth repeat. The remaining 31 states get funded after that, not before.
