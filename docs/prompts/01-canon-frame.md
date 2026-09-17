# Locked generation prompts

Built on the slot architecture: composition → identity → face → eyes → brows → hair → render module → body → wardrobe → lighting → quality tail → negative tail. Anime-2D preset.

**Rule:** every locked detail is restated in full in every prompt. A detail that is not restated is a detail that will drift. Do not "abbreviate because the reference image already shows it".

---

## P0 — Exploration (4 candidates, one prompt, count 4)

Same as P1 below, with this inserted before the quality tail:

> exploring one distinct silhouette variation in jacket panel layout and hair mass arrangement only, proportions and palette unchanged

Purpose: choose a direction. Nothing downstream of this is generated until one candidate is picked.

---

## P1 — Canon frame (the reference for everything after)

One image. Full body, 3/4 left, neutral, **no sword**, no FX. Once approved, its `job_id` is passed as reference media to every later generation.

```
Single full-body character reference of one original male anime character, standing upright
in a neutral straight pose turned three-quarters to the left, both feet flat on the ground
and clearly separated, arms relaxed at the sides, full head-to-toe framing with the whole
body and both feet visible, not cropped, not sitting, pure white seamless background,
professional character sheet presentation, original character in his mid twenties with warm
neutral light skin, slightly angular face with a soft but defined jawline and mature adult
bone structure, not a babyface, medium-large sharp anime eyes in dark graphite brown with a
single thin cyan line along the lower lid, naturally muted catchlights with no oversized
specular glare, strong expressive dark eyebrows set high and thick, very dark charcoal-brown
hair in a medium-short messy asymmetrical cut built from five clean masses - a back mass, a
lit upper crown plane, a heavy front-left forelock, a lighter right sweep, and one short
spike at the crown right that breaks the outline - no loose flyaway strands, clean anime
illustration, crisp lineart, cel-shaded flat colour with soft gradient shadows, consistent
character model-sheet style, athletic slim build with slightly long legs, hands drawn one
step larger than strict anatomy, wearing a short modern techwear jacket ending at the hip
bone in near-black graphite with an asymmetric front closure offset left of centre, four flat
panels per side, a standing collar low enough to leave the neck and jaw readable, no hood,
over a mid-grey inner shirt visible as a collar band and a narrow chest V, fitted dark
graphite trousers with one horizontal seam at mid thigh, low dark boots with a light grey
sole edge, one thin light grey band on each forearm, a small abstract emblem on the left
chest panel - a rounded square outline with the top-right corner notched open, crossed
diagonally at forty-five degrees by a single straight stroke that overshoots both ends and
terminates at its upper end in a small solid square block - no weapon and no sword in this
image, even flat lighting with soft ambient shading and a subtle cool cyan rim along the
upper-left silhouette, high-quality anime key visual, clean vector-like linework, sharp, 4K,
single subject only, exactly one person, only the character in frame, no other people, no
duplicate figures, no mannequin, no reflections, no props, no furniture, no background
objects, empty seamless background, no text, no letters, no watermark, no logos, no frame
borders, no hood, no scarf, no cape, no chains, no straps, no harness, no armour, no chibi
proportions, no 3D render, no Pixar style, no photorealism, no extra fingers, no distorted
anatomy, entirely original character that must not resemble any existing anime character,
costume, hairstyle or franchise
```

**Check before approving:** 6.5-head proportion · collar value clearly lighter than the jacket · emblem legible · feet separated · no hood · both hands intact · hair spike present.

---

## P2 — Sheet A, turnaround

Opening clause replaced with:

```
Character turnaround model sheet, four consistent full-body views in a row - front view,
three-quarter view, side profile, and back view, evenly spaced, identical original character
on all four views, identical height and identical scale across all views,
```

then the full identity/wardrobe/render/negative body of P1, with the canon frame passed as reference media.

## P3 — Sheet B, expressions

```
Character expression sheet, a grid of head-and-shoulders portraits of the same original
character at identical head angle and identical scale, showing neutral, focused, thinking,
confused, surprised, mildly annoyed, determined, satisfied, happy, tired, and sleeping,
```

then identity + hair + render + negative. Wardrobe reduced to collar and shirt only.

## P4 — Sheet D, sword

Object sheet, no character:

```
Object reference sheet of a single original digital sword shown in front view, side view and
three-quarter view at identical length and identical scale, straight blade with no curvature
and a slight distal taper ending in an asymmetric chisel tip, dark metallic blade with a thin
luminous cyan edge line and a brighter pale core inside the glow, a small rectangular bracket
guard - not a disc, not an oval, not a round guard - and a smooth dark charcoal cylindrical
grip with one geometric notch, no wrap, no braid, no cord, no engraving, no symbols, no
characters, clean anime illustration with crisp lineart and cel-shaded flat colour, pure
white seamless background, shown in six energy states in a row at identical geometry -
inactive with no glow, forming from cyan fragments, soft cyan working glow, strong cyan
execution glow with a pale core, a brief red-orange break in the edge line, and a green
success pulse, no character, no hands, no sheath, no scabbard, no text, no letters, no
watermark, no logos, sharp, 4K, entirely original design that must not resemble any existing
anime or game weapon
```

---

## Parameters

- Aspect ratio 16:9 for sheets, 2:3 for the canon frame.
- Preflight with `get_cost: true` before any batch.
- Do not pass `use_unlim` unless explicitly asked.
- Verify the live model catalogue first — aspect ratios, native transparent-background support and reference-media roles were unconfirmed at planning time.
- Never pass the old 3D reference sheet as reference media.
