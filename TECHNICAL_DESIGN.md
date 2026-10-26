# Technical Design — Reusable MkDocs Template

Based on `PRD.md` (2026-10-17).

## 1. Architecture and Dependencies

Static-site pipeline: Markdown (`docs/`) → MkDocs 1.6 → Material theme → `site/` → GitHub Pages (`gh-pages` branch via `mkdocs gh-deploy`).

`requirements.txt`:

```
mkdocs>=1.6,<2
mkdocs-material>=9.5,<10
pymdown-extensions>=10.8,<13
```

Ranges rather than exact pins: they admit the audited versions (1.6.1 / 9.7.7 / 12.1) without forcing an upgrade, and exclude MkDocs 2. Pygments, Markdown, and Jinja2 come in transitively. No plugins beyond MkDocs built-ins (`search`) are required. Environment: a project-local `.venv` (Python 3.12+; developed here on 3.14).

## 2. MkDocs Configuration (`mkdocs.yml`)

Sections, in order, each commented: site identity (`site_name`, `site_description`, `site_url`, `repo_url`, `repo_name`, `edit_uri`) → `theme` → `nav` → `markdown_extensions` → `plugins` → `extra_css` / `extra_javascript` → `validation`.

- `site_url` is set to a placeholder `https://USERNAME.github.io/REPO/` with a comment; `use_directory_urls` left default.
- `strict` is not hard-coded; `--strict` is passed on the CLI (documented), keeping `serve` forgiving.
- `validation: {omitted_files: warn, absolute_links: warn, unrecognized_links: warn, anchors: warn}` so strict mode catches broken links and anchors.
- `exclude_docs` omitted unless needed. `examples/` lives outside `docs_dir`.

## 3. Theme Configuration

```yaml
theme:
  name: material
  language: en
  font: false                # system fonts; no Google Fonts request
  features:
    - navigation.sections
    - navigation.indexes
    - navigation.path        # breadcrumbs
    - navigation.footer      # prev/next
    - navigation.top
    - navigation.tracking
    - toc.follow
    - search.highlight
    - search.suggest
    - content.code.copy
    - content.code.annotate
    - content.tabs.link
    - content.action.edit
```

`navigation.instant` is **not** enabled by default: it requires `site_url` and complicates MathJax re-typesetting. It is documented as optional; the MathJax hook (§5) already supports it via `document$`.

## 4. Light/Dark Mode

Material's native three-state palette (system → light → dark cycle):

```yaml
palette:
  - media: "(prefers-color-scheme)"
    toggle: {icon: material/brightness-auto, name: "Theme: system (click for light)"}
  - media: "(prefers-color-scheme: light)"
    scheme: default
    primary: indigo
    accent: indigo
    toggle: {icon: material/brightness-7, name: "Theme: light (click for dark)"}
  - media: "(prefers-color-scheme: dark)"
    scheme: slate
    primary: indigo
    accent: indigo
    toggle: {icon: material/brightness-4, name: "Theme: dark (click for system)"}
```

The first entry (`(prefers-color-scheme)`) is the "System" state, supported since Material 9.4; Material persists the choice in `localStorage`. No custom switcher or JS.

Custom CSS never sets raw colours outside `[data-md-color-scheme="default"]` / `"slate"` blocks, and otherwise uses `var(--md-*)`.

## 5. MathJax

Markdown side: `pymdownx.arithmatex` with `generic: true`, which wraps math in `<span class="arithmatex">\(…\)</span>` / `<div class="arithmatex">\[…\]</div>` after protecting it from Markdown, so backslashes and underscores are not mangled. Supported input: `$…$`, `$$…$$`, `\(…\)`, `\[…\]`, and `\begin{aligned}…\end{aligned}` blocks.

`docs/javascripts/mathjax.js`:

```js
window.MathJax = {
  tex: { inlineMath: [["\\(", "\\)"]], displayMath: [["\\[", "\\]"]],
         processEscapes: true, processEnvironments: true },
  options: { ignoreHtmlClass: ".*|", processHtmlClass: "arithmatex" }
};
document$.subscribe(() => {
  MathJax.startup.output.clearCache();
  MathJax.typesetClear();
  MathJax.texReset();
  MathJax.typesetPromise();
});
```

`extra_javascript` order: vendored Mermaid + `mermaid-config.js` (§6a), then `javascripts/mathjax.js`, then the MathJax `tex-mml-chtml.js` script from a **pinned** jsDelivr URL (e.g. `https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-mml-chtml.js`). Decision: CDN by default (zero extra tooling); the README documents vendoring the file into `docs/assets/` for offline/privacy use. `document$` is provided by Material and fires on every page load (including instant navigation).

## 6. Markdown Extensions

`admonition`, `attr_list`, `def_list`, `footnotes`, `md_in_html`, `tables`, `toc` (`permalink: true`), `pymdownx.arithmatex` (generic), `pymdownx.betterem`, `pymdownx.details`, `pymdownx.highlight` (`anchor_linenums`, `line_spans`, `pygments_lang_class`), `pymdownx.inlinehilite`, `pymdownx.keys`, `pymdownx.mark`, `pymdownx.snippets` (`base_path: [examples]`, `check_paths: true`), `pymdownx.superfences` (with `mermaid` custom fence), `pymdownx.tabbed` (`alternate_style: true`), `pymdownx.tasklist` (`custom_checkbox: true`).

Mermaid: see §6a.

### 6a. Mermaid

- Markdown: `pymdownx.superfences` custom fence `mermaid` (class `mermaid`), as documented by Material.
- Runtime: Material 9.7.7 loads `https://unpkg.com/mermaid@11/...` (unpinned) **only if** no global `mermaid` exists (`typeof mermaid === "undefined"`). We therefore vendor `mermaid@11.17.2` (`npm pack`, integrity recorded in `docs/assets/vendor/mermaid/VERSION.txt`, MIT licence alongside) and load it via `extra_javascript`, **before** the MathJax CDN script so a slow CDN cannot delay diagrams.
- `docs/javascripts/mermaid-config.js` wraps `mermaid.initialize` (Material calls it itself and resets config, so a second call would be overwritten) to add `securityLevel: "strict"`, `suppressErrorRendering: true` (otherwise Mermaid appends a "Syntax error" graphic to the page body on bad input), and a `themeCSS` fragment using `var(--md-*)` for pie/Gantt titles, legends, and Git-graph labels.
- Theme sync is Material's native behaviour: diagrams re-render on palette change and Material's `themeCSS` maps Mermaid colours to `--md-mermaid-*` variables. No custom switcher.
- Upgrade procedure: `npm pack mermaid@<ver>`, copy `package/dist/mermaid.min.js` and `LICENSE`, update `VERSION.txt`. Stay on 11.x unless Material's expected major changes.

## 7. CSS and JavaScript Organisation

- `docs/stylesheets/extra.css` (single file, sections: content width/typography, tables, code, admonitions/tabs, focus, reduced motion). Rules:
  - Content measure via `.md-grid { max-width: 70rem }` and `.md-typeset { line-height: 1.7 }`.
  - Tables: `.md-typeset__scrollwrap` is already provided by Material (overflow-x); additionally `.md-typeset table:not([class])` keeps `display: table` — verify no override is needed before adding any.
  - Focus: `:focus-visible { outline: 2px solid var(--md-accent-fg-color); outline-offset: 2px }`.
  - Math overflow: `.arithmatex { overflow-x: auto; overflow-y: hidden }` for long display equations on mobile.
  - Reduced motion: `@media (prefers-reduced-motion: reduce)` disable transitions.
  - Only add rules that testing shows are needed; target ≲ 100 lines.
- `docs/javascripts/mathjax.js` as above and `docs/javascripts/mermaid-config.js` (§6a). No other custom JS.

## 8. Navigation Conventions

- Explicit `nav` in `mkdocs.yml` (the subject-specific part). Each section is a folder with `index.md` (`navigation.indexes`), files named in kebab-case with numeric prefixes only when order matters (`01-variables.md`).
- Page front matter optional; each page starts with one `#` heading.
- Standard chapter layout (documented in `docs/authoring/`): Learning objectives → Concept → Syntax → Example + Expected output → Step-by-step → Common mistakes → Exercises → Summary.
- Sample course nav (programming-course example) lives in `mkdocs.yml`; the README explains replacing `nav:`, `docs/curriculum/`, and metadata to create a new subject.

## 9. Local Development Workflow

```
python -m venv .venv
.venv\Scripts\activate          # Windows;  source .venv/bin/activate on Unix
pip install -r requirements.txt
mkdocs serve                    # http://127.0.0.1:8000, live reload
mkdocs build --strict           # CI-grade check
```

## 10. Build and Deployment Workflow

- `mkdocs build --strict` → `site/` (git-ignored).
- `mkdocs gh-deploy --strict` (documented, **never run here**) builds and force-pushes `site/` to `gh-pages`; Pages source set to that branch. A `.nojekyll` is added by `gh-deploy` automatically.
- Paths are relative / `site_url`-derived, so project sub-path hosting works.
- Optional Actions workflow shown in README as a copy-paste snippet, not committed as an active workflow.

## 11. Validation Strategy

| Check | Tool |
|---|---|
| Fresh venv install | `python -m venv` + `pip install -r requirements.txt` + `pip check` |
| Build clean | `mkdocs build --strict`, exit code and output captured |
| Output inventory | assert `site/index.html`, `search/search_index.json`, `stylesheets/extra.css`, `javascripts/mathjax.js` exist |
| Math delimiters | grep built HTML for `class="arithmatex"` and intact `\frac`, `\begin{aligned}`, no `<em>` inside math |
| Config sanity | grep built HTML for MathJax script URL and `data-md-color-media` palette entries |
| Links | strict build + `validation` settings |
| Browser (if available) | render check at 1280/768/375 px, both schemes, MathJax output, copy button, search |

Anything not executed is recorded as unverified in `VALIDATION_REPORT.md`.

## 12. Implementation Order

1. venv + install + `pip check`. 2. `.gitignore`, `requirements.txt`, `mkdocs.yml`. 3. JS/CSS. 4. Sample docs and `examples/`. 5. Build, inspect, fix. 6. Browser checks if possible. 7. `README.md`, `VALIDATION_REPORT.md`; update PRD/TD for any changed decision.
