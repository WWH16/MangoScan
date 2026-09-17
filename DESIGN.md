---
name: MangoScan
description: Field mango disease scanner, lettered like a palengke price board.
colors:
  kraft: "#cda36a"
  kraft-liner: "#b88c52"
  plywood: "#e4d6bd"
  ink: "#1c1814"
  ink-soft: "#3d3124"
  marker-red: "#a01d12"
  marker-green: "#22531d"
  highlighter: "#f6d312"
  tape: "rgb(244 236 214 / 0.86)"
  photo-paper: "#fbf8f1"
  button-ink-text: "#f4e7cf"
typography:
  display:
    fontFamily: "Permanent Marker, Segoe Print, cursive"
    fontSize: "clamp(3rem, 14vw, 5.25rem)"
    fontWeight: 400
    lineHeight: 1.05
    letterSpacing: "0"
  verdict:
    fontFamily: "Permanent Marker, Segoe Print, cursive"
    fontSize: "min(6rem, 12.5cqi)"
    fontWeight: 400
    lineHeight: 0.95
  imperative:
    fontFamily: "Permanent Marker, Segoe Print, cursive"
    fontSize: "clamp(1.9rem, 8vw, 2.75rem)"
    fontWeight: 400
  body:
    fontFamily: "Barlow Semi Condensed, Arial Narrow, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 400
    lineHeight: 1.5
    fontFeature: "\"tnum\" 1"
  lede:
    fontFamily: "Barlow Semi Condensed, Arial Narrow, sans-serif"
    fontSize: "1.1875rem"
    fontWeight: 400
    lineHeight: 1.45
  label:
    fontFamily: "Barlow Semi Condensed, Arial Narrow, sans-serif"
    fontSize: "1rem"
    fontWeight: 600
    letterSpacing: "0.06em"
  button:
    fontFamily: "Barlow Semi Condensed, Arial Narrow, sans-serif"
    fontSize: "1.1875rem"
    fontWeight: 700
    letterSpacing: "0.05em"
rounded:
  board: "3px"
  tape: "1px"
spacing:
  "1": "4px"
  "2": "8px"
  "3": "12px"
  "4": "16px"
  "5": "24px"
  "6": "32px"
  "7": "48px"
  "8": "64px"
components:
  button-ink:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.button-ink-text}"
    typography: "{typography.button}"
    rounded: "{rounded.board}"
    padding: "0 24px"
    height: "56px"
  button-ink-hover:
    backgroundColor: "#000000"
  button-ink-disabled:
    backgroundColor: "{colors.ink-soft}"
  button-tape:
    backgroundColor: "{colors.tape}"
    textColor: "{colors.ink}"
    typography: "{typography.button}"
    padding: "0 24px"
    height: "56px"
  tab-tape:
    backgroundColor: "{colors.tape}"
    textColor: "{colors.ink-soft}"
    typography: "{typography.label}"
    rounded: "{rounded.tape}"
    padding: "8px 16px"
    height: "44px"
  tab-tape-selected:
    textColor: "{colors.ink}"
  board:
    backgroundColor: "{colors.kraft}"
    rounded: "{rounded.board}"
    padding: "48px 24px 32px"
  taped-photo:
    backgroundColor: "{colors.photo-paper}"
    padding: "10px 10px 0"
---

# Design System: MangoScan

## Overview

**Creative North Star: "The Palengke Price Board"**

Every screen is a sheet of kraft corrugated card propped on a plywood table, lettered with a chisel-tip marker the way a market vendor labels a crate of mangoes. The system speaks in two voices: marker lettering for the few words that decide what happens to the fruit (the verdict, the grade and the imperative), and a sturdy condensed grotesk with tabular numerals for everything that has to be read precisely.

The page is light because the tool is used in daylight and under packhouse fluorescents. Depth comes from real materials: fibrous card, translucent masking tape with torn ends, and white photo paper. State is shown with marks a person would make with a pen (a check, a circle, a strike-through or a highlighter swipe), never with colour alone. Density is low: one event per phone viewport.

**Key Characteristics:**
- Kraft card on plywood, never white app chrome.
- Marker lettering only for verdicts, imperatives and the screen's single instruction.
- Condensed grotesk with tabular numerals for every reading.
- Masking tape holds tabs, secondary buttons and photos.
- Drawn marks (check, circle, strike, arrow, highlighter) carry state.

## Colors

A restrained material palette: kraft and plywood grounds, one near-black ink, two marker colours that encode the verdict, and one highlighter for emphasis.

### Primary
- **Marker Ink** (ink): all body text, marker lettering, primary buttons and focus rings.
- **Highlighter Yellow** (highlighter): the single emphasis swipe behind the imperative, text selection and viewfinder corner guides. Never a text colour.

### Secondary
- **Marker Red** (marker-red): disease verdicts (anthracnose, stem-end rot), the grade strike and circle, and error notes. Only for large marker text on kraft, or for text on the light note paper.
- **Marker Green** (marker-green): the healthy verdict, the grade check and completed pipeline steps. Large text only on kraft.

### Neutral
- **Kraft Card** (kraft): the face of every board, textured by the `static/img/kraft.png` tile.
- **Kraft Liner** (kraft-liner): the line under the fluted top edge of each board.
- **Plywood Table** (plywood): the page ground under the boards.
- **Soft Ink** (ink-soft): secondary text on kraft, pending tabs, and the struck-out grade.
- **Masking Tape** (tape): tabs, secondary buttons, and the strips holding photos.
- **Photo Paper** (photo-paper): the border around every photo and note.

### Named Rules
**The Verdict Colour Rule.** Red and green belong to the verdict. They never decorate, and they only ever appear as large marker text or as drawn marks.

**The One Swipe Rule.** Highlighter yellow appears once per screen: behind the imperative, or as the viewfinder guides.

## Typography

**Display Font:** Permanent Marker (with Segoe Print, cursive), self-hosted.
**Body Font:** Barlow Semi Condensed (with Arial Narrow, sans-serif), self-hosted, weights 400 to 700.

**Character:** A loose chisel marker set against a disciplined, narrow grotesk. The marker says what to do; the grotesk proves it.

### Hierarchy
- **Display** (400, clamp(3rem, 14vw, 5.25rem), 1.05): the scan screen's one instruction, rotated −1.5°.
- **Verdict** (400, fitted to the card with container units, 0.95, uppercase): the class name, filling the board width on one line and rotated −2°.
- **Imperative** (400, clamp(1.9rem, 8vw, 2.75rem)): one short command under a highlighter swipe.
- **Lede / Action** (400–500, 1.1875rem, 1.45): the sentence that explains the screen or the treatment, at most 44ch.
- **Body** (400, 1.0625rem, 1.5, tabular numerals).
- **Label** (600–700, 1rem, 0.04–0.08em tracking, uppercase): tabs, buttons, the grade label and section toggles.

### Named Rules
**The Few Marker Words Rule.** Marker lettering never runs longer than one short line, except the scan-screen instruction. Paragraphs, readings and controls are always set in Barlow.

**The Tabular Rule.** Every number is shown with tabular numerals.

## Layout

A single centred board, at most 620px wide, on the scan screen. The verdict screen is one column on phones. From 900px up it becomes two columns: the verdict board on the left (1.05fr) and the taped evidence photo on the right (1fr), with the photo sticky. The content container is at most 1120px, with safe-area-aware side gutters of 12–16px.

On touch devices the scan board fills the viewport up to 660px tall and pushes the photo picker to the bottom. "Take photo" is the last and largest control, at thumb height. Spacing follows a 4px base: 4, 8, 12, 16, 24, 32, 48, 64. Boards pad 48/24/32px on phones and 64/48/48px from 600px up.

## Elevation & Depth

Depth is material: paper on a table. Boards cast one soft two-part shadow. Photos and notes cast a smaller one. Tape has no shadow; it is translucent and sits on top.

### Shadow Vocabulary
- **Board** (`box-shadow: 0 1px 1px rgb(70 45 15 / 0.18), 0 12px 28px -8px rgb(70 45 15 / 0.38)`): every kraft board.
- **Paper** (`box-shadow: 0 1px 2px rgb(60 40 15 / 0.25), 0 8px 18px -6px rgb(60 40 15 / 0.35)`): taped photos and notes.
- **Ink button** (`box-shadow: 0 8px 16px -8px rgb(30 20 8 / 0.55)`): the primary button.

### Named Rules
**The Declare Once Rule.** Each surface gets either a shadow or a hairline, never both.

## Shapes

Corners are nearly square (3px on boards, 1px on tape) because cut cardboard and tape are square. Every board has a fluted top edge: an SVG corrugation profile over dark liner. Tape strips have torn, zig-zag ends drawn with an SVG mask, and sit slightly rotated (−8° to +6° on photos, ±1° on tabs). Photos sit on white paper at −0.6°.

## Components

### Buttons
- **Shape:** near-square (3px); 56px tall; the "Take photo" button is 72px tall.
- **Ink (primary):** near-black fill, cream uppercase Barlow 700 label, and a stroke icon on the left.
- **Hover / Active:** the fill goes to pure black; pressing moves the button down 2px. Disabled buttons fill with soft ink and show the progress cursor.
- **Tape (secondary):** a torn-end masking-tape strip with an ink label. It gets lighter on hover.
- **Text link:** ink text with a 2px underline and 4px offset (used for "Remove").

### Tabs
- **Style:** masking-tape labels, rotated −1° and +1.2°, with an uppercase Barlow 600 label.
- **State:** the selected tab turns full ink and gains a skewed 3px marker underline, which draws in from the left. The unselected tab stays soft ink. Tabs use WAI-ARIA tablist behaviour with arrow, Home and End keys.

### Boards
- **Corner Style:** 3px.
- **Background:** kraft plus the fibre tile.
- **Shadow Strategy:** the Board shadow.
- **Internal Padding:** 48/24/32px on phones and 64/48/48px from 600px up.

### Taped Photo
White photo-paper frame with 10px padding and two torn tape strips at the top. The caption row holds the file name (ellipsised), the size, and actions.

### Notes
Light paper slips (#fbf3e2) with the Paper shadow, rotated −0.4°. Error notes use marker red, a drawn warning icon, and a 44px close button.

### Verdict Block (signature)
The class name in marker fills the board. Beside the "Grade" label:
- **Diseased:** a struck-through "A" and a circled grade letter.
- **Healthy:** a checked "A".

Below sits the imperative on a highlighter swipe, then the treatment sentence. Motion runs once: the word is revealed (700ms), the swipe grows (from 350ms), then the marks draw (from 450–650ms). All of it collapses under reduced motion.

### Readings
Price-board rows: a soft-ink label, a 2px dotted leader, and a bold right-aligned value.

### Pipeline List
The five real stages, each with its count on the right:
1. Resize, 128 × 128.
2. HSV histogram, 32,768.
3. GLCM, 20.
4. Hu moments, 7.
5. RBF SVM, 3 classes.

Pending steps show a Barlow numeral. The current step shows a drawn arrow and a travelling marker underline. Finished steps show a drawn green check.

## Do's and Don'ts

### Do:
- **Do** set the verdict, the grade marks and the imperative in Permanent Marker, and everything else in Barlow Semi Condensed.
- **Do** show state with drawn marks (check, circle, strike, arrow, underline) as SVG, in the same stroke language.
- **Do** keep touch targets at least 44px, and make the main action 56–72px tall and last in the thumb zone.
- **Do** hold photos and secondary controls with torn-end tape.
- **Do** keep numbers tabular and name units in plain words ("33.9% of surface", "48 °C").

### Don't:
- **Don't** use Unicode glyphs or emoji as icons or state marks.
- **Don't** put red or green on small text over kraft; they fail contrast there.
- **Don't** use white app cards, gradient text, or zero-blur offset shadows.
- **Don't** burn text labels into the detection overlay; the page carries the words.
- **Don't** show the old Cursor-style stage names (Thinking, Grep, Read, Edit, Done); show only the real pipeline.
