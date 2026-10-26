# Validation Report

Date: 2026-10-17 · Platform: Windows 11 · Browser: Google Chrome (headless, driven over the DevTools protocol) · Nothing was committed, pushed, or deployed.

## Environment and dependency versions (project `.venv`)

Python **3.14.8** (the only interpreter installed; Python 3.12 was **not** available and **not** tested).

| Package | Version |
|---|---|
| mkdocs | 1.6.1 |
| mkdocs-material | 9.7.7 |
| mkdocs-material-extensions | 1.3.1 |
| pymdown-extensions | 12.3 |
| Markdown | 3.11.1 |
| Pygments | 2.21.0 |
| Jinja2 | 3.1.6 |
| MathJax (CDN, pinned) | 3.2.2 |
| Mermaid (vendored, pinned) | 11.17.2 |

`requirements.txt` ranges: `mkdocs>=1.6,<2`, `mkdocs-material>=9.5,<10`, `pymdown-extensions>=10.8,<13`.

## Commands executed and results

| Command | Result |
|---|---|
| `python -m venv .venv` and `pip install -r requirements.txt` | succeeded |
| `pip check` | "No broken requirements found." |
| `mkdocs build --strict` (final run, after all changes) | **exit 0**, no `WARNING`/`ERROR` lines, 63 files in `site/`, built in ~1.2 s |

**Upstream notice:** every build prints a boxed "Warning from the Material for MkDocs team" about MkDocs 2.0. It is plain output, not a log warning; strict mode still exits 0. It was not suppressed. Project-specific warnings: none.

## Build-level checks (executed)

- Built HTML contains `class="arithmatex"` spans; `\frac`, `\begin{aligned}`, `\begin{bmatrix}` survive intact; no `<em>` inside math.
- Output has `index.html`, `search/search_index.json`, `stylesheets/extra.css`, `javascripts/mathjax.js`, `javascripts/mermaid-config.js`, `assets/vendor/mermaid/{mermaid.min.js,LICENSE,VERSION.txt}`.
- Palette entries `(prefers-color-scheme)`, `light`, `dark` present in the generated HTML.
- `docs/examples/mermaid.md` build output has 10 `class="mermaid"` blocks and the Mermaid source text (e.g. `flowchart TD`).
- Code blocks produce `language-java/c/cpp/python/javascript/sql/bash/yaml/json/typescript/text` classes.
- Internal links/anchors: checked by strict build with `validation` set to `warn`.

## Browser tests (executed in headless Chrome, served from `site/` by a static Node server)

Note: an early run used Python's `http.server`; it stalled/reset connections on Windows and produced false failures (bundle response after 19 s, `ERR_CONNECTION_RESET`). Those results were discarded and all results below come from the Node static server.

**MathJax / pages (36 page loads: 6 pages × 3 widths × light/dark)**
- Math rendered (`mjx-container` present: 30 on the math page, 10 on the sample chapter, 4 on the home page); 0 MathJax error nodes; inline, display, matrix, aligned, softmax, and math inside an admonition and tabs all appeared in screenshots (light and dark viewed).
- Widths 1280 / 768 / 375 px: no page-level horizontal overflow and no overflowing content elements outside intentional scroll containers.
- Copy buttons present on code pages (13 on the code page, 5 on the sample chapter).

**Theme**
- Palette button cycled System → Light → Dark → System (stored `__palette` index 0→1→2→0).
- Emulated `prefers-color-scheme` light/dark gave `default`/`slate` schemes. Screenshots of math, components, code, and Mermaid pages in dark and light were inspected visually. **Contrast was judged visually, not measured with a contrast tool.**

**Search**
- Typing "sigmoid" with real key events returned "2 matching documents" (math page, home page). Note: Material listens for `keyup`, so synthetic `input` events give no results; this was a test-harness issue, not a site defect.

**Mermaid** (`/examples/mermaid/`, 4 loads: light/dark × 1280/375 px)
- Vendored `mermaid.min.js` and `mermaid-config.js` were requested from the local server; no request to `unpkg.com` was observed (request log from the earlier run: external hosts were only `cdn.jsdelivr.net` for MathJax and `api.github.com` from `repo_url`).
- All 9 valid diagrams rendered in every run (flowchart, sequence, class, state, ER, Gantt, pie, Git graph, mindmap), viewed in screenshots in light and dark; mobile width has no page overflow.
- Live theme change (light → dark via the palette button) re-rendered the diagram in dark colours.
- Malformed diagram: stays as source text in its own block; the rest of the page renders; one console `Parse error` exception is thrown per page load. The "Syntax error" graphic Mermaid appends to the page body by default is suppressed (`suppressErrorRendering`).
- Contrast problems found and fixed during testing: pie title/legend and Gantt title in dark mode, Git-graph commit/branch labels (`mermaid-config.js`).

## Tests not performed / unverified

- Python 3.12 install and build.
- Real mobile/tablet devices (only emulated viewports).
- Keyboard-only navigation and focus-indicator appearance (CSS added; not exercised).
- Quantitative contrast measurement (WCAG ratios) and screen-reader behaviour.
- Safari/Firefox/Edge (Chrome only).
- Mermaid rendering of every diagram type in the "System" palette state without emulation, and tablet width for Mermaid.
- Offline behaviour: Mermaid is vendored but MathJax is **not**; offline math is unsupported and untested.
- `mkdocs gh-deploy` and GitHub Pages hosting: intentionally not run. Deployed-path asset loading was not tested (only root-path local serving; paths are relative).
- `mkdocs serve` (live server) was not run to completion.

## Remaining limitations

- MathJax needs network access (CDN).
- Setting `repo_url` makes the browser call `api.github.com` on every page.
- The 3.5 MB Mermaid script is downloaded on every page (cached after the first load).
- Gantt and sequence diagram text is small at phone width; Git-graph label colours are fixed only for the first two branches.
- Material for MkDocs 9.x is in maintenance mode upstream (MkDocs 2.0 notice).
- Test artifacts remain in `.shots/` (git-ignored); delete it manually when no longer needed (automatic deletion was blocked by a safety check).
