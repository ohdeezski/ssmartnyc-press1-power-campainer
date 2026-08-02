# Street Smart NYC — Brand & Design System (Single Source of Truth)

This file is the canonical reference. Web (Phase 1) and Android (Phase 2) both
inherit from it. Changing a value here must propagate to both platforms.

## 1. Brand Architecture (dual identity)
- PUBLIC / MARKETING brand:  "Street Smart NYC"
    - Used on: app stores, landing pages, OG images, email footers, paid ads,
      anything customer-facing that must read as a legit business.
- INTERNAL / PRODUCT codename: "57R337 $M4R7 NYC"  (leet stylization)
    - Used on: in-app chrome (nav bar wordmark, loading screens, operator HUD,
      error pages flavor text). Pure UI flair — never in store listings.
- Rule: the launcher icon + login screen show the PUBLIC wordmark; once inside
  the authenticated console, the codename may appear as the top-bar mark.

## 2. Logo System
Generated concepts (kept in app/static/brand/raw/):
- 01_monogram_ss_signal.png — PRIMARY EMBLEM (SS + broadcast arcs). Use for
  favicon, nav mark, print lockups, Android launcher basemark.
- 02_wordmark.png          — WORDMARK "STREET SMART NYC". Use for login/landing
  and footer.
- 03_owl_tower_mascot.png  — MASCOT / character mark. Secondary only (about page,
  empty states, docs hero). Not in dense UI.
- 04_appicon_squircle.png  — APP ICON. Android adaptive foreground + web PWA icon.
Final production assets (SVG + multiple PNG sizes) are produced in Phase 1.5.

## 3. Color Tokens
Core (always available):
  --bg-primary   #050505   near-black canvas
  --bg-card      #101418   surface / panel
  --border       #1CEFFF   primary hairline border (cyan)
  --accent       #00E5FF   primary cyan (actions, links, glow)
  --accent-2     #7B2EFF   purple (secondary / category)
  --success      #00FF99   green
  --warning      #FFAA00   amber
  --danger       #FF3366   red
  --text-1       #E0E3E8   primary text
  --text-2       #888      secondary text
  --text-3       #555      muted
Semantic aliases (Tailwind/Compose map to these):
  primary=accent, surface=bg-card, on-surface=text-1, outline=border,
  error=danger, secondary=accent-2.
Contrast: text-1 on bg-primary = ~15.8:1 (AAA). accent on bg-primary for large
text only (cyan small text fails AA — use text-1 for body, accent for emphasis/
borders/icons).

Status palette — the 9 campaign states, always rendered as a colored dot +
uppercase label. Canonical hexes (sync to base.html Tailwind `status.*` colors
and main.css `--status-*`; do NOT reuse these for decorative accents):
  --status-gray   #6B7280   not_started   (in queue)
  --status-blue   #4DA6FF   preparing     (prep / validation)
  --status-cyan   #00D4FF   connecting    (provider link-up)
  --status-green  #00FF99   running       (live / success)
  --status-yellow #FFAA00   waiting       (paused / hold)
  --status-orange #FF8800   retrying      (retry / degraded)
  --status-purple #7B2EFF   transferring  (press-1 / handoff)
  --status-red    #FF3366   failed        (error / down)
  --status-white  #FFFFFF   finished      (terminal OK)
Status states are the ONLY consumers of these hues — semantic success/warning/
danger remain #00FF99/#FFAA00/#FF3366.

## 4. Typography
- Display / UI: Inter (loaded via Google Fonts). Weights 400/500/600/700/800.
- Monospace / data: JetBrains Mono (loaded via Google Fonts), fallback
  'Courier New', monospace. Used for IDs, counts, latencies, code — never for
  prose.
- Scale: h1 1.5rem, h2 1.25rem, h3 1.1rem; body 0.875rem; label 0.75rem;
  code 0.75rem. Uppercase + letter-spacing 0.05em on headings/labels (tactical).
- Android: same Inter via Compose font resource; Material3 type roles map to
  the scale above.

## 5. Iconography
- Material Symbols Outlined (weight 400, fill 0/1) for UI glyphs.
- Icons render in `currentColor` so they inherit token colors.
- Accent icons get subtle glow (drop-shadow) only at 20–24px sizes.

## 6. Spacing & Radius
- Base unit 4px. Gutter 16px, panel padding 12px, page margin 24px.
- Radius: DEFAULT 2px (sharp/tactical), lg 4px, xl 8px, full = pill (9999px).
- Android: Material3 default corners (12–16px) are acceptable for cards to feel
  native; keep 2px only for inline chips/segmented controls to preserve identity.

## 7. Motion
- Pulse for "live" indicators: 1.5s ease-in-out infinite.
- Scanline overlay: fixed, opacity 0.1, pointer-events none (decorative only).
- Transitions: 150ms color/background, 200ms transform. No long ease-in entrances.

## 8. Voice / Tone
- Operator/HUD framing: "System: Operational", "Secure link established".
- Flavor only; never block function with cute copy.

## 9. Component Library
Reusable Jinja partials live in `app/templates/components/` (global template
folder, includable from any page). They render with Tailwind tokens from the
base.html config — never hardcode a hex in a partial. Contract: every partial
documents its parameters in a Jinja comment header. Shared list:
- status_badge, stat_card, progress_bar, pipeline_bar, checklist_item,
  setup_card, event_feed, status_ribbon, health_panel, verify_row, audio_row,
  toast, modal_confirm, data_table, stepper, empty_state.
Rule: if the same markup appears on three pages, it becomes a partial.

---
PROPAGATION: edit tokens here -> sync to (a) app/modules/ui/templates/ui/base.html
<Tailwind config + :root vars>, (b) app/static/css/main.css, (c) Phase 2 Android
theme. Keep all three byte-consistent for hex values.
