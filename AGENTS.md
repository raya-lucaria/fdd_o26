# Repository Guidelines

## Project Structure & Module Organization

This repository is the authored source for the Spanish-language ITAM course *Fuentes de Datos — Otoño 2026*. Course pages live in the ordered `course/` tree; every rendered directory has a `0_index.md`. Colocate learning objects in `_official/`, media in `_assets/`, and reviewed execution output in `_reviewed/`. `skins/` contains visual tokens. `tools/` contains generators and pytest guardrails. `artifact/` is generated output: never edit or commit it.

## Build, Test, and Development Commands

Run content guards from this repository:

```bash
python3 -m pytest tools/ -q
```

Run Raya from the sibling framework checkout:

```bash
cd ../raya_lucaria
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya validate ../fdd_o26
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya build ../fdd_o26
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya preview ../fdd_o26
```

Use `validate` for fast feedback; `build` also validates; `preview` serves the generated site.

## Coding Style & Naming Conventions

Write student-facing prose, titles, and instructions in Spanish. Keep technical IDs, object types, filenames, tags, and skin tokens in English. Numeric prefixes define order only; durable links use stable IDs such as `[[memoria-y-datos]]`. Use four spaces in Python and two spaces for nested YAML. Quote YAML values containing colons. Raw HTML is disabled, so use CommonMark and Raya directives.

## Testing Guidelines

Add focused `tools/test_*.py` guards for editorial invariants and generated assets. Run the full suite before committing. For visual changes, also build and inspect desktop and mobile Chromium views. Edit SVG generators—not generated SVG output—when a generator is the source of truth. Every image requires alt text and a row in `_assets/CREDITOS.md`.

## Commit & Pull Request Guidelines

Follow history’s Conventional Commit shape: `feat(unidad-3): ...`, `fix(unidad-3): ...`, or `chore(unidad-3): ...`. Keep commits focused. Pull requests must summarize the learner-visible change, list validation commands, link relevant issues, and include screenshots for navigation, layout, or image changes. Never include `.env`, API keys, caches, or `artifact/`.
