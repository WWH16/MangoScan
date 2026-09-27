# Product

## Register

product

## Users

Mango farmers are the primary users. They use MangoScan on a phone, usually a budget Android phone, outdoors in daylight in the orchard or at the packing area, often with one hand while holding the fruit. Many are more comfortable reading Filipino than English, and mobile data can be slow.

Secondary users are agricultural inspectors and packinghouse sorters, who use the same flow. The thesis panel and researchers read the technical detail on a laptop; that detail is kept behind "Technical details" so it never gets in the farmer's way.

## Product Purpose

MangoScan checks one mango from one photo (phone camera, live viewfinder, or a saved file) and says in plain words whether the fruit is healthy, has anthracnose, or has stem-end rot, and what to do with it. Under the hood it extracts 32,795 handcrafted features (3D HSV colour histogram, GLCM texture, Hu shape moments) and classifies them with an RBF Support Vector Machine, then marks the affected area on the photo and estimates defect coverage.

Before classifying, it screens out photos it cannot judge (no single fruit in frame, too blurry, too dark or too bright) and asks for a better photo instead of guessing.

The site opens on a landing page that explains the three answers in plain words; the scanner itself lives at `/scan`, which the installed app opens directly. Anyone can scan without an account. People who sign up (email and password, through Supabase Auth) get every scan saved with its photos under "My scans", can delete single scans, and can delete their whole account. The app can be installed to the phone's home screen.

## Brand Personality

- **Plain and trustworthy:** simple words, one clear answer, no hype.
- **Calm tool, not a toy:** a clean shadcn/ui-style interface with nothing decorative.
- **Field-ready:** readable in direct sun, big touch targets, fast on slow data.

## Anti-references

- Flashy AI apps with neon gradients and glowing effects.
- Dashboards full of charts a farmer does not need.
- Confidence numbers or technical terms shown to farmers without a plain-language answer.

## Design Principles

1. **One answer first:** the verdict, what to do, and the grade come before any technical reading.
2. **Field-first usability:** high contrast, touch targets of at least 44px (56px for the main action), main action at thumb height, photos shrunk on the phone before upload.
3. **Honest limits:** never classify a photo the model cannot judge; say why and how to retake it.
4. **Actionable advice:** every verdict comes with practical sorting or treatment guidance.
5. **Transparent when asked:** the real pipeline stages and measurements are available under "Technical details" for the thesis panel.

## Accessibility & Inclusion

- English and Filipino, chosen in Settings (the gear icon in the header) and remembered on the phone.
- WCAG AA contrast on white; muted text and borders one step darker than shadcn's defaults for sunlight.
- Minimum 44px touch targets on phones.
- Keyboard-navigable tabs and dialogs; focus returns to the trigger when a dialog closes.
- Reduced-motion safe: the scan line, spinners and dialog animations collapse.

## Privacy

- Scanning without an account stores nothing on the server; the result exists only in the page.
- Saved scans and photos are private to their owner (Row Level Security and a private Storage bucket).
- Users can delete any scan, or their whole account with all scans and photos, in line with the Philippine Data Privacy Act (RA 10173).
