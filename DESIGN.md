---
name: MangoScan
description: Field mango disease scanner in a plain shadcn/ui style, tuned for phones in daylight.
colors:
  background: "#ffffff"
  foreground: "#09090b"
  card: "#ffffff"
  muted: "#f4f4f5"
  muted-foreground: "#52525b"
  subtle-foreground: "#71717a"
  border: "#d4d4d8"
  input: "#d4d4d8"
  primary: "#18181b"
  primary-hover: "#27272a"
  primary-foreground: "#fafafa"
  secondary: "#f4f4f5"
  secondary-hover: "#e4e4e7"
  ring: "#71717a"
  destructive: "#dc2626"
  destructive-soft: "#fef2f2"
  success: "#15803d"
  success-soft: "#f0fdf4"
  destructive-border: "#fca5a5"
  destructive-text: "#b91c1c"
  success-border: "#bbf7d0"
  success-text: "#166534"
typography:
  title:
    fontFamily: "Geist, ui-sans-serif, system-ui, sans-serif"
    fontSize: "clamp(1.75rem, 7vw, 2.25rem)"
    fontWeight: 600
    lineHeight: 1.15
    letterSpacing: "-0.025em"
  verdict:
    fontFamily: "Geist, ui-sans-serif, system-ui, sans-serif"
    fontSize: "clamp(2.25rem, 10vw, 3rem)"
    fontWeight: 700
    lineHeight: 1.05
    letterSpacing: "-0.035em"
  imperative:
    fontFamily: "Geist, ui-sans-serif, system-ui, sans-serif"
    fontSize: "1.375rem"
    fontWeight: 600
  card-title:
    fontFamily: "Geist, ui-sans-serif, system-ui, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 600
  body:
    fontFamily: "Geist, ui-sans-serif, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "Geist, ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 500
  small:
    fontFamily: "Geist, ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 400
  body-lg:
    fontFamily: "Geist, ui-sans-serif, system-ui, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 500
  body-sm:
    fontFamily: "Geist, ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 400
  dialog-title:
    fontFamily: "Geist, ui-sans-serif, system-ui, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 600
  caption:
    fontFamily: "Geist, ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 500
  mono:
    fontFamily: "Geist Mono, ui-monospace, monospace"
    fontSize: "0.8125rem"
    fontWeight: 400
rounded:
  sm: "6px"
  md: "8px"
  lg: "12px"
  pill: "999px"
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
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.primary-foreground}"
    rounded: "{rounded.md}"
    height: "48px"
  button-primary-large:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.primary-foreground}"
    rounded: "{rounded.md}"
    height: "56px"
  button-outline:
    backgroundColor: "{colors.background}"
    textColor: "{colors.foreground}"
    rounded: "{rounded.md}"
    height: "40px"
  card:
    backgroundColor: "{colors.card}"
    rounded: "{rounded.lg}"
    padding: "24px"
  input:
    backgroundColor: "{colors.background}"
    rounded: "{rounded.md}"
    height: "48px"
  badge-destructive:
    backgroundColor: "{colors.destructive}"
    textColor: "#ffffff"
    rounded: "{rounded.pill}"
  badge-success:
    backgroundColor: "{colors.success-soft}"
    textColor: "#166534"
    rounded: "{rounded.pill}"
---

# Design System: MangoScan

## Overview

**North Star: "shadcn, plainly."** The user asked for the shadcn/ui look, kept simple. Every screen uses the same few parts: white background, zinc greys, cards with a fine border and a small shadow, one dark primary button, pill badges, tabs, a progress bar and an accordion. Nothing decorative.

Two things differ from stock shadcn, on purpose, because MangoScan's users are farmers on phones outdoors:
- Muted text is zinc-600 (not zinc-500) and borders are zinc-300 (not zinc-200), so text and dividers survive sun glare.
- Touch targets are larger: inputs and buttons are 48px tall, the main action ("Take photo", "Check this mango", "Scan a mango") is 56px, and links are at least 44px tall.

## Colors

- **Neutrals (zinc):** background white, foreground zinc-950, muted zinc-100 for tab tracks and photo letterboxes, muted-foreground zinc-600 for secondary text, border and input zinc-300.
- **Primary:** zinc-900 fill with near-white text. One primary button per screen.
- **Destructive (red-600):** the "Disease found" badge, the "Disease" tag in My scans, error alerts and field errors, and "Delete this scan".
- **Success (green):** the "No disease found" badge and the confirmation alert (soft green background, dark green text).

## Typography

Geist for everything, self-hosted (variable, 100–900). Geist Mono only for the pipeline step counts. Numbers use tabular figures.

- **Page title** (600, clamp(1.75rem, 7vw, 2.25rem), -0.025em): "Scan a mango.", "My scans."
- **Verdict** (700, up to 3rem, -0.035em): the class name on the result screen.
- **Imperative** (600, 1.375rem): the order ("Quarantine.").
- **Card title** (600, 1.5rem): the account forms.
- **Body** (400, 1rem, 1.6) with muted-foreground for descriptions.
- **Label** (500, 0.875rem): form labels and tabs.

## Layout

One column on phones, two columns from 900px (content max 1120px, 16px gutters). A sticky 60px header with a bottom border holds the logo tile (it links to the scanner for signed-in users and to the landing page for everyone else), the wordmark, a short tagline on desktop, an outline "Log in" or "My scans" button, and a gear button for Settings.

- **Landing (`/`):** for first-time visitors; the installed app opens the scanner at `/scan` directly, so returning farmers skip it; the header logo links back here for visitors who are not signed in. A larger title (up to 3.25rem, -0.035em), one sentence, the 56px "Scan a mango" button and a green-check "Free. No account needed." line; beside it on desktop (below it on phones) the three real sample photos with their verdict pills. Then "How it works": three numbered steps (dark 36px number circles joined by a 1px line on phones; on desktop the number and text stay sticky beside the picture) that carry one real anthracnose scan through the viewfinder frame, the checking card (plain-language checklist, one scan-line pass when it scrolls into view) and the real marked-up result card. Then "The three answers" (bordered list: thumbnail, name, order, action), "Good to know" (a plain definition list with lucide icons and underlined links, not a card grid), a muted closing panel with the button again, and the technical accordion last. Section titles are 600, up to 1.875rem.
- **Scan (`/scan`):** title, one sentence, then a card with the photo tip, "Take photo" and two links ("Choose a saved photo", "Use live camera"). On desktop an example photo sits on the right in a rounded bordered frame; it is replaced by the farmer's photo once chosen. Under everything, an accordion "How MangoScan checks a photo".
- **Result:** badge, verdict, order, action, "Scan another mango", then the photo (tabs: Marked up / Original) and a readings card with the grade and a defect-coverage progress bar. "Technical details" is an accordion holding confidence, hue, saturation, photo size and the pipeline.
- **Account pages:** one centred card, at most 420px wide.
- **My scans:** a bordered list with thumbnail, verdict, date and order per row, and a red "Disease" pill when the fruit is not healthy.
- **Photo problems:** when a photo has no clear fruit, or is too blurry, too dark or too bright, the scan page returns with a red alert saying what to fix. No result is shown.
- **Languages:** every string exists in English and Filipino; Settings switches and remembers the choice for a year.
- **Settings:** reached from the gear icon, always the last item in the header; language is chosen only here (the header has no language link). One column of cards, max 640px, under the title and a one-line description: Language (segmented English | Filipino), Install MangoScan (the browser's install prompt when offered, otherwise manual steps, or "installed"), and for signed-in users Profile (name field and Save), Password (current then new, and Change password), Log out (a row card with an outline button) and a red-bordered Delete account card whose button opens the alert dialog. Logged-out visitors see an Account card with Log in and Create account instead. Log out and Delete account live only here.
- **Installable:** a web app manifest and icons (dark tile with the white mango, maskable variant) let farmers add MangoScan to the home screen; offline, pages fall back to a "No internet connection" card with "Try again".

## Components

- **Card:** 1px border, 12px radius, small shadow, 24px padding.
- **Button (primary):** zinc-900, 8px radius, 48px tall (56px for the main action), label centred with an optional lucide icon.
- **Button (outline):** white with a 1px border and small shadow; used for the header's account link.
- **Link:** underlined text with a light underline that darkens on hover; always at least 44px tall.
- **Input:** 48px tall, 1px border, 8px radius; focus shows a 3px grey ring. Errors turn the border red and show a message with an alert icon under the field. Password fields have a "Show" toggle inside the input.
- **Badge:** pill, 13px semibold; red solid for disease, soft green for healthy.
- **Tabs:** muted track with 4px padding; the selected tab is white with a small shadow.
- **Progress:** 8px pill track in zinc-200 with a zinc-900 fill.
- **Accordion:** full-width row with a chevron that rotates when open, closed by default.
- **Alert:** 8px radius box; red tint for errors, green tint for confirmations.
- **Alert dialog:** deleting a saved scan opens a native `<dialog>` card (max 440px) over a 60% black backdrop: title "Delete this scan?", a one-line consequence, then an outline "Cancel" (focused first) and a red "Delete scan". Buttons stack full-width on phones with Delete on top; Escape or a backdrop tap cancels.
- **Button (loading):** a button that sends a form shows a turning ring (1em, 2px, open on one side) in place of its icon, a short waiting label ("Please wait…", "Saving…", "Deleting…", "Checking…") and stays disabled until the next page arrives. The ring keeps turning slowly under reduced motion, because it reports status.
- **Button (loading):** a button that sends a form shows a turning ring (1em, 2px, open on one side) in place of its icon, a short waiting label ("Please wait…", "Saving…", "Deleting…", "Checking…") and stays disabled until the next page arrives. The ring keeps turning slowly under reduced motion, because it reports status.
- **Toast:** server messages (saved, logged out, deleted, errors) appear as toasts, not inline boxes: a white card with an 8px radius, a 1px border and a large soft shadow, a green check or red alert icon, the message and a 44px close button. Error toasts use the red tint and stay until closed; others close after 6 seconds, pausing while touched, hovered or focused. Phones stack them under the header; from 600px they sit bottom right, 380px wide. Page scripts add their own with `MangoToast.show(text, type)`.
- **Type-to-confirm:** deleting the account asks the user to type their name (their email when no name is set), shown in a muted bordered chip. "Delete my account" stays disabled until the text matches (spaces trimmed, capital letters ignored); the server checks the same rule and refuses a mismatch with an error toast.
- **Dialog:** the checking state is a centred card over a 60% black overlay, with the photo, a white scan line and the pipeline steps (spinner for the current step, checks for finished ones).

## Motion

Short and functional only: the dialog fades and scales in (200ms), the pipeline spinner turns, the scan line sweeps the photo, and progress bars fill once on load. All motion collapses under reduced motion.

## Do's and Don'ts

- **Do** keep to the shadcn parts above; add a new part only in the same idiom.
- **Do** keep one primary button per screen and keep it at thumb height on phones.
- **Do** keep muted text at zinc-600 or darker and borders at zinc-300.
- **Don't** add gradients, colored backgrounds, decorative illustration or extra accent colors.
- **Don't** nest cards inside cards.
- **Don't** use color alone for the verdict; the badge always carries words and an icon.
