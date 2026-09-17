# Decisions log

Every entry here is binding on all downstream art, rigging and code.
Nothing gets generated, drawn or rigged against a decision that is still `OPEN`.

Date of record: 2026-09-17.

## LOCKED

| # | Decision | Value | Why |
|---|----------|-------|-----|
| D1 | Production method | **Locked master + rig.** AI image generation produces *design reference only*. One clean master is built from it, rigged, and all states are posed from that rig. | The brief's own "no drift between poses" rule is unreachable by re-prompting a model per pose. A rig is also the only route to the ~30-layer requirement, the skin system and clean small-size output. |
| D2 | Sword & sheath | **No sheath.** The blade materialises from cyan energy in 6–8 frames and dematerialises the same way. | Removes an undesigned layer from all 40 states, removes 2 draw-order swaps per walk cycle, removes bespoke art in 5 states, and deletes the "katana on the back" silhouette that sits closest to the IP negative list. |
| D3 | v1 scope | **9 core states**, validated in the real app before the remaining 31 are funded. `idle, thinking, working, tool-call, error, success, sleep, appear, disappear`. | Contrast over a dark IDE, event-rate behaviour and error-fatigue are all unknowns that only real usage answers. Buying 40 animations before answering them is the expensive order. |
| D4 | Proportions & size contract | **6.5 heads.** Full body at ≥180 px character height. At 120 px the renderer switches to a waist-up crop, not a smaller full body. | At 7 heads / 120 px the eye is ~4 px and the pupil ~2 px — the 11-expression sheet would be invisible at the most common render size. 6.5 heads buys +17% face area and is still far from chibi. |

## RECOMMENDED, PENDING CONFIRMATION

| # | Decision | Recommendation | Note |
|---|----------|----------------|------|
| D5 | Animation runtime | **Rive only**, with a generated PNG/WebP frame-sequence fallback for constrained surfaces. | Live2D has no documented 360°/back-view path. Spine's runtime agreement is not an OSI-style licence and bars downstream modification without a per-user editor seat — incompatible with a forkable public repo. Lottie has no programmatic draw-order API, which the cross-body blade needs. |
| D6 | Licensing split | Code under MIT or Apache-2.0. Art under **CC BY 4.0** in `LICENSE-ASSETS`. Name + emblem reserved in `TRADEMARK.md`. | Raw AI output is very likely not copyrightable in the US (Thaler v. Perlmutter, D.C. Cir. 2025; cert denied Mar 2026), so an NC/ND art licence buys an unenforceable restriction while blocking the community skin system and Debian/Fedora packaging. Trademark law has no human-authorship requirement — that is where the real leverage is. |
| D7 | Mirroring | Character is designed **mirror-tolerant**: emblem centred, hair part readable from both sides, sword hand not load-bearing for identity. Locomotion mirrors with `scaleX = -1`. | The alternative is ~35 extra drawables for something nobody tracks on a 180 px sprite. |
| D8 | Adaptive rim light | Ship a **manual light/dark rim toggle** + OS theme following. Screen sampling behind the window is opt-in only. | Any screen capture on macOS triggers the screen-recording permission prompt, which is far too heavy an ask for a mascot. |
| D9 | Character name | Undecided. Needs to be short, pronounceable, trademark-clearable, and not a third-party AI vendor's name. | The app/extension stores reject third-party trademarks in names and listings. Name must be cleared before the repo is public — renaming after launch is the expensive path. |
| D10 | Commercial tier | Answer now even if the answer is "not yet". | It determines whether an NC licence is coherent, whether the image service's revenue threshold triggers, and how store reviewers read the listing. Retrofitting a commercial path onto community contributions later is effectively impossible. |

## EXPLICITLY REJECTED FROM THE ORIGINAL BRIEF

- **"Riggable in Rive / Spine 2D / Live2D / After Effects / CSS."** These are five separate rigging passes with no interchange format, and two of them cannot do what the brief asks. → D5.
- **"~30 layers."** That is a node list, not an art list. Realistic count is ~70–80 drawables per view before expression and hand variants. See `03-production-pipeline.md`.
- **Passing the attached 3D reference sheet to an image model as reference media.** It would import its 3D shading, its hoodie and its infinity emblem — all three on the negative list. It is used as a *written* list of which states to cover, nothing more.
- **Naming specific franchise characters in prompts, commit messages or public design docs.** Use structural descriptions of what to avoid instead. A public paper trail of "make it like X but legally different" is self-harm in any dispute.
- **A grid sheet with baked-in text labels as a production asset.** It is a communication artefact only. Production assets are single-pose, transparent, fixed-canvas, fixed-anchor.
