# Brand Rules — Digital Castle S.P.C
# قواعد الهوية — القلعة الرقمية ش.ش.و
#
# Binding for every human and every autonomous agent writing code in this repo.
# Scope: the PARENT ENTERPRISE only (reports, proposals, invoices, contracts,
# audits, letterheads, corporate site). Client projects and downstream SaaS
# ventures have their own product identities — do NOT apply this file to them.

## 1. Source of truth
- All colour, type, spacing and legal strings come from `brand-kit/tokens/`.
- Import `brand-kit/tokens/dc-tokens.css` once at the app root, or the Tailwind
  preset at `brand-kit/tokens/tailwind.preset.js`. Use `tokens.ts` in JS/TS.
- NEVER hardcode a hex value, font name, or the company's legal/contact details.
  If a value is missing from the tokens, add it there — not inline.

## 2. Colour
- Body text is always `--dc-ink` on `--dc-paper` or `--dc-canvas`.
- `--dc-blue` (#0025FF) is an ACCENT: rules, eyebrows, links, the grand-total
  rule, focus rings. Cap it at roughly 5% of any surface. Never body text,
  never a large fill.
- `--dc-cyan` (#08F9F2) is legal ONLY on `--dc-keep` / `--dc-ink` grounds.
  It fails contrast on white. Do not use it on light backgrounds.
- The blue→cyan gradient belongs to the logo mark and to 2px divider rules on
  dark grounds. Never a page background, never behind text, never on a button.
- Status colours are functional signals only. Never decorative, never brand.
- No shadows beyond `--shadow-doc` on document sheets. No glow, no neon.

## 3. Type
- English: Spectral (display) + Plus Jakarta Sans (text) + IBM Plex Mono (figures).
- Arabic: Almarai (display, matches the logo wordmark) + IBM Plex Sans Arabic (text).
- Request only shipped weights — the browser fakes anything else:
  Spectral 300/400/600 · Plus Jakarta Sans 400/500/600/700 ·
  Almarai 300/400/700/800 · IBM Plex Sans Arabic 400/500/600 · IBM Plex Mono 400/500.
- Arabic is NEVER uppercased and NEVER letter-spaced. Where English uses tracked
  caps, Arabic uses the same size at Almarai 700 in `--dc-mist`.
- Arabic line-height = Latin × 1.15 (body 1.62 → 1.90).
- Never justify text. Never set body copy below 13px on screen or 9.5pt in print.

## 4. Logo
- Render it only through `<DigitalCastleLogo />` or an `<img>` pointing at
  `brand-kit/logo/`. Three cuts: primary (light grounds), reversed (dark
  grounds), mark (cube only, ≥40px).
- Never recolour, rotate, outline, stretch, add effects to, or redraw the mark.
- Never place the primary (dark-wordmark) cut on a dark background — use reversed.
- Clear space: 1× the cube width on all four sides. Minimum lock-up: 160px / 34mm.

## 5. Geometry
- `border-radius: 0` everywhere. Nothing in this system is rounded.
- Borders are 1px `--dc-frost`; emphasis rules are 2px `--dc-blue`.
- Space on the 4px baseline (`--dc-1`…`--dc-8`). Layout with flex/grid + gap.

## 6. Official documents
- Every generated document carries the corporate header (logo + document class
  eyebrow, EN and AR) and the legal footer (legal name, C.R. 1197389, VAT id,
  contact, page n/total, confidentiality notice). Use `<DocumentHeader />` and
  `<DocumentFooter />`; do not hand-roll them.
- A4, margins 18/20/20/20mm, 12-column grid, prose max 8 columns.
- Tables: hairlines only — no zebra striping, no fills, no outer border.
  Numeric columns are mono, tabular-nums, right-aligned.
- One callout per section, maximum.
- Legal disclaimers are pulled from `dcLegal`, never retyped.

## 7. Copy
- Answer first, reasoning after, risk named before the reader finds it.
- No hype adjectives, no exclamation marks, no emoji, no unsourced statistics.
- Every figure carries a unit, a date or a stated assumption.
- Arabic legal name is «القلعة الرقمية ش.ش.و» — without the word «شركة».

## 8. Review checklist before merging any UI
- [ ] No hardcoded hex, font-family, or contact string in the diff.
- [ ] Cyan used only on dark grounds; gradient only on the mark.
- [ ] Arabic not uppercased, not tracked, line-height ≥ 1.9.
- [ ] All font weights exist in the family.
- [ ] border-radius is 0.
- [ ] Documents carry the statutory footer.
