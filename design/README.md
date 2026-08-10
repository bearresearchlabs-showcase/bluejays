# BLUEJAYS Design System

The benchmark's brand, as code. One JSON source of truth compiles to CSS custom properties; a component layer builds on the tokens; a living showcase renders every piece. This is the **artifact-facing brand system** — it unifies the three ad-hoc styles the benchmark's documents grew organically (light academic landing, dark engagement pages, OpenAI-docs deliverable layout). It is complementary to `apps/web/DESIGN_SYSTEM.md`, which is the React component library internal to the docs application.

## Files

| File | Role |
|------|------|
| `tokens.json` | **Source of truth** — colors (light + dark values per token), type stacks and scale, spacing, radii, layout constants |
| `build_tokens.py` | Deterministic compiler: `tokens.json` → `tokens.css`, then bundles `bluejays.css` (same input ⇒ byte-identical output; generated files are committed) |
| `tokens.css` | Generated custom properties. Theme model: full light palette on `:root`; dark redefined under `@media (prefers-color-scheme: dark)` guarded by `:root:not([data-theme="light"])`; `:root[data-theme="dark"]` wins over both so an explicit toggle beats the system preference in either direction |
| `components.css` | The component layer (`bj-*` classes): hero/wordmark, buttons, stat tiles, status cards, badges, tables, quote/news/code furniture, the docs sidebar layout, and the formalism figures (tuple band, pipeline band) |
| `bluejays.css` | The bundle pages link (tokens + components) |
| `showcase.html` | Living style guide with a theme toggle — every class rendered from the bundle, nothing inline |

## Use

```html
<link rel="stylesheet" href="design/bluejays.css">
<body class="bj">           <!-- prose pages -->
<body class="bj bj-docs">   <!-- sidebar/docs layout -->
```

Rebuild after editing tokens: `python3 design/build_tokens.py` (stdlib only). Never edit `tokens.css` or `bluejays.css` by hand — the header says so and the build will overwrite you.

For the Tailwind v4 app (`apps/ingest`), the tokens adopt directly: paste the emitted custom properties into an `@theme` block, or reference them as `var(--brand-jay)` in arbitrary values — no plugin needed.

## Rules

1. **Tokens only.** No hex literals in component CSS or artifact pages; if a color is missing, add it to `tokens.json` and rebuild.
2. **Status colors are semantic, not decorative.** `ok`/`warn`/`bad`/`note` carry the evidence taxonomy used across the benchmark's documents (verified / environment-blocked or vacuous / defect / forward-looking). Do not repurpose them.
3. **Both themes always.** Every token carries a light and a dark value; a component that looks wrong in one theme is a bug.
4. **Existing artifacts migrate opportunistically.** `index.html`, `mdp-tuple-architecture.html`, and `mdp-architecture-db6.html` predate this system and keep their inline styles until a deliberate migration pass; new artifacts start from `bluejays.css`.

---

**Last Updated:** 2026-08-06
