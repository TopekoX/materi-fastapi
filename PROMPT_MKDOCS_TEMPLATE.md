# Prompt: Build a Reusable Modern MkDocs Documentation Template

## Role

Act as a Senior Documentation Platform Engineer, Technical Writer, UI/UX Designer, and Python Developer.

Your task is to design and implement a reusable MkDocs template for creating structured educational materials and technical documentation across multiple subjects, including Java, C, C++, Python, JavaScript, Machine Learning, Data Science, and other technical topics.

The result must be a maintainable, modern, reusable documentation platform, not just a single documentation website.

## 1. Primary Objective

Build a reusable MkDocs template that can be copied or cloned into separate repositories for different educational subjects.

Each new project should require only minimal changes to:
- Project title and description.
- Documentation navigation.
- Course or subject content.
- Branding and optional theme settings.
- Deployment configuration.

The shared template must provide a consistent user experience across all projects.

## 2. Required Workflow

Work in the following phases.

### Phase 1 — Project Audit

Before making changes:

1. Inspect the existing repository and directory structure.
2. Inspect `mkdocs.yml`, `requirements.txt` or other dependency files, existing Markdown files, CSS, JavaScript, and deployment scripts.
3. Identify the installed Python, MkDocs, Material for MkDocs, and extension versions.
4. Identify existing functionality that must be preserved.
5. Check whether the repository is already used for GitHub Pages deployment.
6. Document compatibility issues and implementation risks.

Do not overwrite existing work without understanding its purpose.

If the repository already contains an implementation, improve it incrementally rather than replacing it unnecessarily.

### Phase 2 — Create the PRD

Create `PRD.md` before implementing the template.

The PRD must contain:

1. Product overview and vision.
2. Problem statement.
3. Target users and use cases.
4. Product goals and non-goals.
5. Functional requirements.
6. Non-functional requirements.
7. UI/UX requirements.
8. Technical stack and architectural decisions.
9. Proposed directory structure.
10. Accessibility and responsive design requirements.
11. Testing and acceptance criteria.
12. Deployment requirements.
13. Risks, assumptions, and constraints.

Separate mandatory features from optional enhancements.

### Phase 3 — Technical Design

Create `TECHNICAL_DESIGN.md` based on the approved PRD.

Document:
- Architecture and dependencies.
- MkDocs configuration.
- Theme configuration.
- Light/dark mode implementation.
- MathJax configuration.
- Markdown extensions.
- CSS and JavaScript organization.
- Navigation conventions.
- Local development workflow.
- Build and deployment workflow.
- Validation strategy.

Avoid unnecessary dependencies and custom JavaScript when native Material for MkDocs features can satisfy the requirements.

### Phase 4 — Implementation

Implement the template according to the PRD and technical design.

Do not skip requirements or silently replace them with weaker alternatives.

### Phase 5 — Validation and Documentation

Test the implementation, fix issues, and document how to reuse the template.

Update the PRD or technical design if an implementation decision changes a documented requirement.

## 3. Technology Stack

Use the following baseline:

- Python 3.12-compatible environment.
- MkDocs 1.6.x.
- Material for MkDocs 9.x.
- `pymdown-extensions`.
- MathJax for mathematical expressions.
- Custom CSS only where necessary.
- Minimal custom JavaScript.
- Git and GitHub Pages compatibility.

Inspect the actual installed dependencies before changing them.

Preserve compatible pinned dependency versions when possible. Do not upgrade the entire stack unnecessarily.

Use compatible version constraints and do not introduce `mkdocs>=2`.

## 4. UI/UX Requirements

Create a modern, clean, professional documentation interface suitable for long-form educational content.

Required features:

- Responsive desktop, tablet, and mobile layouts.
- Clear typography and comfortable line spacing.
- Modern sidebar navigation with hierarchical sections.
- Search functionality.
- Breadcrumbs and previous/next page navigation.
- Clear visual hierarchy for headings.
- Consistent spacing and content width.
- Readable tables and horizontally scrollable wide tables on small screens.
- Attractive code blocks with syntax highlighting.
- Copy-to-clipboard buttons for code blocks.
- Accessible focus indicators and keyboard navigation.
- Appropriate contrast in both light and dark themes.
- Consistent styling for admonitions, tabs, diagrams, and examples.
- No unnecessary visual effects that reduce readability.
- No broken links, overlapping elements, or clipped content.

Use Material for MkDocs features wherever possible.

Do not introduce a separate frontend framework for the documentation interface.

## 5. Light and Dark Mode

Configure three theme preferences:

- System.
- Light.
- Dark.

Requirements:

1. Users can switch themes using the theme selector.
2. The system preference is respected when System is selected.
3. Theme colors remain consistent across all components.
4. Code blocks, tables, admonitions, search, navigation, and mathematical content remain readable.
5. Custom CSS must use theme-aware variables or appropriate light/dark selectors.
6. Avoid hard-coded colors that cause contrast problems in either theme.
7. Ensure the selected theme works with the standard Material for MkDocs theme behavior.

Use Material's native palette configuration instead of implementing a redundant theme switcher.

## 6. LaTeX and Mathematical Expressions

Configure MathJax so mathematical notation renders correctly in Markdown documents.

Support inline mathematics:

`The sigmoid function is $\sigma(x) = \frac{1}{1+e^{-x}}$.`

Support display mathematics:

`$$`

`f(x) = \frac{1}{\sqrt{2\pi}}e^{-x^2/2}`

`$$`

The implementation must also support:

- Fractions and exponents.
- Subscripts and superscripts.
- Summations and integrals.
- Matrices and vectors.
- Greek letters.
- Multi-line aligned equations.
- Machine Learning and Deep Learning formulas.
- Mathematical symbols within educational explanations.

Use MathJax with the necessary Markdown extensions and compatible JavaScript configuration.

Verify that Markdown processing does not break LaTeX delimiters or escape backslashes incorrectly.

Test both inline and display equations in the built website.

If diagrams or equations are used inside admonitions, tabs, or other supported Markdown containers, verify rendering in those contexts as well.

Document the supported syntax and any limitations.

## 7. Programming Documentation Features

Support technical documentation for multiple programming languages.

The template must accommodate:

- Java.
- C.
- C++.
- Python.
- JavaScript and TypeScript.
- SQL.
- Bash and shell commands.
- YAML and JSON.
- Other languages supported by the selected syntax highlighter.

Required documentation patterns:

1. Concept explanations.
2. Syntax examples.
3. Code blocks with language-specific highlighting.
4. Expected output.
5. Step-by-step tutorials.
6. Exercises and practice problems.
7. Common mistakes and troubleshooting.
8. Mathematical explanations.
9. Tables and comparison guides.
10. Learning objectives and chapter summaries.

Use Markdown and Material extensions for admonitions, content tabs, and code highlighting where appropriate.

Do not create a custom execution engine for running code examples.

## 8. Reusable Directory Structure

Design a clear directory structure that separates configuration, documentation, assets, and deployment files.

Use a structure similar to:

    mkdocs-template/
    ├── mkdocs.yml
    ├── requirements.txt
    ├── README.md
    ├── PRD.md
    ├── TECHNICAL_DESIGN.md
    ├── docs/
    │   ├── index.md
    │   ├── getting-started/
    │   │   └── index.md
    │   ├── curriculum/
    │   │   └── index.md
    │   ├── stylesheets/
    │   │   └── extra.css
    │   ├── javascripts/
    │   │   └── mathjax.js
    │   └── assets/
    └── examples/
        ├── programming/
        └── mathematics/

Adjust this structure when the existing repository or the actual MkDocs configuration requires a different arrangement.

The `examples/` directory may be outside the MkDocs `docs_dir` so example files are not unintentionally published as documentation.

Keep the configuration easy to understand and maintain.

Do not create an unnecessarily complex multi-repository framework or introduce a custom template engine unless there is a clear technical justification.

## 9. Configuration and Customization

Make the template easy to adapt to different subjects.

The main configuration should clearly identify:

- Site name.
- Site description.
- Site URL, when applicable.
- Repository URL and edit links, when applicable.
- Theme palette.
- Markdown extensions.
- Navigation.
- Custom CSS and JavaScript.
- Deployment settings.

Use a documented example configuration for a programming course.

Do not make subject-specific content, navigation, or branding inseparable from the shared theme.

Do not add empty configuration abstractions solely for hypothetical future requirements.

## 10. Documentation Content

Provide realistic sample content demonstrating the main capabilities.

Include:

- A landing page.
- A getting-started page.
- A sample curriculum page.
- A programming example with syntax highlighting and copy buttons.
- An inline LaTeX equation.
- A display LaTeX equation.
- An admonition.
- A table.
- A tabbed content example if supported by the chosen extensions.

Keep the sample material concise and focused on validating the template.

Do not generate a full Java, C, or C++ curriculum as part of this task.

## 11. GitHub Pages Compatibility

Support deployment through:

`mkdocs gh-deploy`

Requirements:

- Keep the build compatible with GitHub Pages.
- Document the repository configuration needed for deployment.
- Explain how to configure the canonical site URL.
- Ensure the theme assets, CSS, JavaScript, and MathJax configuration load correctly after deployment.
- Do not assume a custom domain exists.
- Do not execute a production deployment unless explicitly requested.

Preserve any existing deployment scripts and their safeguards.

## 12. Testing and Acceptance Criteria

The implementation is complete only when the following criteria have been addressed.

### Build and Dependencies

- Dependencies install successfully in the supported environment.
- `mkdocs build --strict` completes without errors or warnings.
- No unnecessary dependency upgrades are introduced.
- No broken internal navigation links remain.

### UI

- Desktop, tablet, and mobile layouts are checked.
- Light and dark themes are checked independently.
- Theme-specific contrast issues are resolved.
- Navigation, search, code copy buttons, and tables work.
- No obvious horizontal overflow or clipped components occur, except intentional horizontal scrolling for wide tables or code blocks.

### LaTeX

- Inline mathematics renders correctly.
- Display mathematics renders correctly.
- Fractions, subscripts, superscripts, and aligned equations are tested.
- LaTeX works on representative educational pages.
- JavaScript configuration and Markdown delimiters remain valid after the build.

### Deployment

- Build output contains the expected assets and pages.
- Deployment instructions are complete.
- No deployment is executed without authorization.

Use automated checks where practical and browser-based verification when available.

If browser testing is unavailable, state exactly which tests were performed and which remain unverified. Do not claim a test passed without evidence.

## 13. Scope and Safety Constraints

- Do not commit changes to Git.
- Do not deploy the website.
- Do not delete existing user content.
- Do not overwrite existing files without inspection.
- Do not modify unrelated projects or repositories.
- Avoid unnecessary changes to existing folder structures.
- Keep custom CSS and JavaScript minimal and maintainable.
- Do not introduce external fonts or third-party services without a clear requirement.
- Document any limitations or assumptions.
- Never report a successful test unless it was actually executed.

## 14. Expected Deliverables

Deliver the following:

1. `PRD.md`.
2. `TECHNICAL_DESIGN.md`.
3. A working MkDocs template.
4. A documented dependency file.
5. A reusable theme configuration.
6. Responsive theme-aware CSS.
7. MathJax configuration.
8. Representative sample documentation.
9. `README.md` containing installation, local development, customization, and deployment instructions.
10. A validation report summarizing completed tests, results, and remaining limitations.

## 15. Final Report

When implementation is complete, report:

- What was inspected.
- What was created or modified.
- Important technical decisions.
- How to install dependencies.
- How to run the local server.
- How to build the documentation.
- How to create a new subject-specific documentation project.
- How to deploy to GitHub Pages.
- Which acceptance tests passed or failed.
- Any remaining limitations.

Begin with Phase 1: audit the repository and report the findings.

Then create the PRD and technical design before implementing the template. Continue through the remaining phases unless a genuine blocker requires clarification.

Prioritize correctness, reusability, maintainability, and verified results over unnecessary visual complexity.