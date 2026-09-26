---
name: MangoScan
description: Field mango disease scanner, set like a monochrome type-specimen sheet.
colors:
  paper: "#f3f2ee"
  paper-raised: "#fbfaf7"
  paper-sunk: "#e9e7e1"
  ink: "#121212"
  ink-2: "#363636"
  ink-3: "#5a5a5a"
  rule: "rgb(18 18 18 / 0.16)"
  rule-strong: "rgb(18 18 18 / 0.42)"
  blue: "#1d3fc0"
  blue-deep: "#152f96"
  blue-wash: "#e6eaf7"
typography:
  headline:
    fontFamily: "JetBrains Mono, ui-monospace, monospace"
    fontSize: "clamp(2.25rem, 10vw, 4rem)"
    fontWeight: 500
    lineHeight: 1.12
    letterSpacing: "-0.03em"
  verdict:
    fontFamily: "Archivo, Arial Narrow, sans-serif"
    fontSize: "min(6rem, 17cqi)"
    fontWeight: 800
    fontStretch: "88%"
    lineHeight: 0.92
    letterSpacing: "-0.035em"
  imperative:
    fontFamily: "JetBrains Mono, ui-monospace, monospace"
    fontSize: "clamp(1.625rem, 6vw, 2.25rem)"
    fontWeight: 500
    lineHeight: 1.15
  body:
    fontFamily: "JetBrains Mono, ui-monospace, monospace"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.6
    fontFeature: "\"tnum\" 1, \"zero\" 1"
  lede:
    fontFamily: "JetBrains Mono, ui-monospace, monospace"
    fontSize: "1.0625rem"
    fontWeight: 400
    lineHeight: 1.65
  label:
    fontFamily: "JetBrains Mono, ui-monospace, monospace"
    fontSize: "0.8125rem"
    fontWeight: 600
    letterSpacing: "0.12em"
  button:
    fontFamily: "JetBrains Mono, ui-monospace, monospace"
    fontSize: "1rem"
    fontWeight: 600
  small:
    fontFamily: "JetBrains Mono, ui-monospace, monospace"
    fontSize: "0.75rem"
    fontWeight: 400
  wordmark:
    fontFamily: "Archivo, Arial Narrow, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 700
  step:
    fontFamily: "JetBrains Mono, ui-monospace, monospace"
    fontSize: "0.9375rem"
    fontWeight: 600
  reading-value:
    fontFamily: "JetBrains Mono, ui-monospace, monospace"
    fontSize: "1.125rem"
    fontWeight: 700
  reading-title:
    fontFamily: "JetBrains Mono, ui-monospace, monospace"
    fontSize: "1.375rem"
    fontWeight: 600
  fine:
    fontFamily: "JetBrains Mono, ui-monospace, monospace"
    fontSize: "0.875rem"
    fontWeight: 400
rounded:
  control: "2px"
  knob: "50%"
spacing:
  "1": "4px"
  "2": "8px"
  "3": "12px"
  "4": "16px"
  "5": "24px"
  "6": "32px"
  "7": "48px"
  "8": "64px"
  "9": "96px"
components:
  button-primary:
    backgroundColor: "{colors.blue}"
    textColor: "#ffffff"
    typography: "{typography.button}"
    rounded: "{rounded.control}"
    padding: "0 24px"
    height: "56px"
  button-primary-hover:
    backgroundColor: "{colors.blue-deep}"
  tab:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    typography: "{typography.button}"
    rounded: "{rounded.control}"
    height: "44px"
  tab-selected:
    backgroundColor: "{colors.blue-wash}"
    textColor: "{colors.blue-deep}"
  status-alert:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    typography: "{typography.label}"
    height: "36px"
---

# Design System: MangoScan

## Overview

**Creative North Star: "The Specimen Sheet"**

MangoScan is set like a type foundry's specimen page: warm off-white paper, black ink, one cobalt accent, hairline rules and a monospace voice. The mango takes the place of the giant specimen glyph, and every reading is shown like a variable-font axis: a label, a value, and a track with a knob at the value. The user supplied the reference (a monochrome variable-typeface marketing page) and it is pinned.

The page is light because farmers use it outdoors on phones in daylight. Ink on paper is the highest-contrast pairing available in sun. Depth is almost absent: hairlines separate everything, and only the reading overlay casts a shadow. Density is low on the phone (one task per screen) and rises to a three-column specimen layout on wide screens.

**Key Characteristics:**
- Paper and ink, with cobalt blue as the only colour in the interface.
- JetBrains Mono for everything read or tapped; Archivo only for the verdict word and the wordmark.
- Hairline grids and rules instead of cards.
- Readings drawn as axis tracks with a knob at the value.
- One button per screen; technical detail folded into a drawer.
- The user's photos always keep their real colour; only the decorative sample specimen is printed in greyscale.

## Colors

### Primary
- **Ink** (ink): all text, outline buttons, knobs on secondary readings, and the inverted "Disease found" block.
- **Cobalt** (blue): the one accent. Primary buttons, the selected tab, focus rings, text selection, the defect-coverage knob and fill, and the scan line. Never used for body text.

### Neutral
- **Paper** (paper): the page ground everywhere.
- **Raised paper** (paper-raised): photo frames, notes and the reading overlay panel.
- **Sunk paper** (paper-sunk): letterbox behind photos that do not fill their frame.
- **Ink 2** (ink-2): secondary text (10.9:1 on paper).
- **Ink 3** (ink-3): scale ends, pending pipeline steps and small metadata (6.3:1 on paper).
- **Rule / Rule strong**: hairlines between rows and around grids and controls.

### Named Rules
**The One Accent Rule.** Cobalt is the only hue in the interface. The verdict is never carried by red or green: it is carried by the words, the icon, and the inverted ink block for disease.

**The True Photo Rule.** The farmer's photos and the marked-up evidence keep their real colour. Greyscale is only for the decorative sample specimen on the scan screen.

## Typography

**Mono:** JetBrains Mono (variable, 400 to 800), self-hosted.
**Display:** Archivo (variable width 62 to 125 %, weight 100 to 900), self-hosted.

**Character:** A disciplined monospace carries instructions, readings and controls, like the spec text of a type specimen. A heavy, slightly condensed grotesk carries the few words that act as the specimen: the verdict and the big numbers.

### Hierarchy
- **Headline** (Mono 500, clamp(2.25rem, 10vw, 4rem), 1.1, -0.03em): the scan screen's instruction, "Scan a mango."
- **Verdict** (Archivo 800 at 88 % width, fitted to its column with container units up to 6rem, 0.92): the class name, on one line.
- **Imperative** (Mono 500, clamp(1.625rem, 6vw, 2.25rem)): the order under the verdict ("Quarantine.").
- **Lede / Action** (Mono 400, 1 to 1.0625rem, 1.65, at most 46ch): the sentence that explains the screen or the treatment.
- **Label** (Mono 700, 0.8125rem, 0.1em, uppercase): the status block only.

### Named Rules
**The Tabular Rule.** Every number uses tabular figures and a slashed zero.

**The Specimen Word Rule.** Archivo appears only for the verdict and the wordmark. Everything else is Mono.

## Layout

Two columns from 900px up, one column below. The content container is at most 1180px with 16px safe-area gutters.

- **Scan screen:** the words and controls on the left (headline, one lede sentence, the photo tip, "Take photo", then two text links: "Choose a saved photo" and "Use live camera"); a large square photo frame on the right that shows a greyscale example until the farmer picks a photo, then their photo in colour.
- **Result screen:** the verdict, order, action and "Scan another mango" on the left, followed by the grade and the defect-coverage reading; the marked-up photo on the right, sticky.
- **Technical detail is folded away.** Under each screen, one "More" drawer holds what only researchers need: how the pipeline works on the scan screen, and model confidence, hue, saturation, photo size, the pipeline and the Otsu note on the result screen.

On touch phones the scan screen's first view ends with "Take photo" at thumb height, and after a photo is chosen the "Check this mango" button sticks to the bottom edge. Spacing follows a 4px base: 4, 8, 12, 16, 24, 32, 48, 64, 96.

## Elevation & Depth

Flat. Hairlines (1px rule or rule-strong) separate rows, grid cells and columns. The only shadow is on the reading overlay panel (`0 2px 4px rgb(18 18 18 / 0.06), 0 24px 48px -16px rgb(18 18 18 / 0.28)`), because it floats over the page. Knobs use a 3–4px paper-coloured ring so they cut through the track.

## Shapes

Corners are 2px on buttons, tabs and frames. Knobs and the grade dot are circles. Icons are drawn SVG with square caps and mitred joins at 1.75px stroke.

## Components

### Buttons
- **Primary:** cobalt fill, white Mono 600 label on the left, stroke icon on the right; 56px tall, 72px for "Take photo", "Check this mango" and "Capture and check". The arrow icon nudges right on hover.
- **Text link:** ink text with a 1px underline at 5px offset (used for "Remove").

### Tabs
Only on the result screen, to switch the evidence photo between "Marked up" and "Original": two equal outlined cells, 44px tall. The selected one gets a 1.5px cobalt border, a cobalt wash and cobalt text. The scan screen has no tabs; the live camera is a text link with a "Back to photo" link inside it.

### Text links
Secondary choices are underlined Mono 600 text links at 44px height, never a second button, so each screen has exactly one button.

### Status block
"No disease found" is an outlined block with a check icon. "Disease found" is the one inverted block on the page (ink fill, paper text, warning icon), so it reads at a glance in sun.

### Readouts (signature)
Each reading is a row: label left, value right in bold Mono with its unit small, then a track (1px rule) with a fill and a knob at the value, and the scale ends underneath. The visible reading is defect coverage, in cobalt, under a plain "Grade" row. Confidence, hue (0–180) and saturation (0–255) use the same rows in ink inside the "Technical details" drawer.

### Specimen
On wide scan screens, a square frame shows the sample mango in greyscale, multiplied into the paper, captioned "Example photo". When the farmer picks a photo, it replaces the sample in full colour and the caption becomes the file name.

### Pipeline
The five real stages: resize to 128 × 128, HSV histogram (32,768), GLCM (20), Hu moments (7), RBF SVM (3 classes). Always a list with hairlines between rows. In the drawers every step shows an ink check. In the checking overlay, pending steps show their number in ink 3, the current step a pulsing cobalt dot, finished steps an ink check.

### "More" drawer
A full-width `details` element between two strong hairlines, 56px summary row with a plus that turns into a cross when open.

### Reading overlay
A raised paper panel over a 94 % paper veil. The chosen photo sits in a 4:3 frame with a cobalt scan line sweeping top to bottom, above the pipeline list.

### Notes
Raised paper with a 1.5px ink border and a drawn warning icon. The close button is 44px.

## Motion

One authored moment per screen:
- **Result:** the verdict word animates its variable weight from 200 to 800 and its width from 112 % to 88 % over 1.1s, while the readout knobs slide from zero to their values (900ms, from 300ms).
- **Reading:** the scan line sweeps the photo and the steps tick off.

All motion collapses under reduced motion; the scan line then rests at mid-photo.

## Do's and Don'ts

### Do:
- **Do** keep the interface to paper, ink and cobalt.
- **Do** carry the verdict with words, icons and the inverted block, never with hue alone.
- **Do** show every reading as an axis track with its scale ends.
- **Do** keep touch targets at least 44px, and make the main action 56–72px tall and last in the thumb zone.
- **Do** keep numbers tabular and name units in plain words ("11.2% of surface", "48 °C").

### Don't:
- **Don't** add red, green or any second accent to the interface.
- **Don't** desaturate the farmer's photo or the marked-up evidence.
- **Don't** use cards with shadows, gradient text, or a kicker label above a heading.
- **Don't** use Unicode glyphs or emoji as icons or state marks.
- **Don't** burn text labels into the detection overlay; the page carries the words.
