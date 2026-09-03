# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A **course source repository**, not an application. It holds authored Markdown/YAML for the ITAM course *Fuentes de Datos — Otoño 2026*, consumed by the Raya Lucaria framework (Glintstone static builder) to generate a static site published to GitHub Pages at **https://rayalucaria.org/fdd_o26/**.

The published site comes from `raya.yaml`, `course/`, `skins/`, and `.github/workflows/pages.yml`. `tools/` holds image generators plus the pytest guards that protect them; it never renders.

Course-facing content (page prose, titles, summaries, task instructions) is written in **Spanish**. Technical identifiers — `id`, `type`, `authority`, `scope`, filenames, tags, skin token names — stay in **English**.

The sibling course `~/itam/ia_o26` is the reference implementation of the same contract; when a pattern here is unclear, check how that repo does it.

## The build toolchain lives in a sibling repository

The `raya` CLI is not installed here. It lives at `~/itam/raya_lucaria` (a separate git repo) and is invoked from there with this repo's path as an argument:

```bash
cd ~/itam/raya_lucaria
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya validate ~/itam/fdd_o26
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya build    ~/itam/fdd_o26
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya preview  ~/itam/fdd_o26   # validate + build + serve
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya artifacts inspect ~/itam/fdd_o26/artifact
```

`validate` is the fast feedback loop — broken links, missing IDs, bad official-object scopes, skin contrast failures — without building. `build` implies validate. `preview` serves `artifact/site/` at `http://127.0.0.1:8000/index.html`, with an inspection view at `/_raya/inspect/index.html`.

**Version pinning matters.** `.github/workflows/pages.yml` pins a SHA of `raya-lucaria/raya-lucaria.github.io`, and the reusable workflow checks the framework out at exactly that SHA. That pin **is** the framework version building the site. This repo requires the native course calendar, which landed in `b0ec778`; do not move the pin backwards.

## `artifact/` is generated — never edit it

`artifact/` is gitignored build output (`manifest.json`, `data/*.json`, `site/`). Regenerate with `raya build`. To change what appears on the site, change `course/`, `raya.yaml`, or `skins/`.

Also gitignored and absent from a clean clone: `.env` (only `OPENAI_API_KEY`, for `tools/gen_ilustraciones.py`).

## Authoring contract

Enforced by `raya validate`. These are the rules most likely to bite:

**Ordering and stable identity.** Numeric prefixes on files and directories (`1_introduccion/`, `2_etl_elt.md`) define authoring order *only*. They are stripped from rendered URLs, labels, and stable IDs — `course/2_pipeline_de_datos/2_etl_elt.md` publishes at `/pipeline-de-datos/etl-elt/`. Durable references use the frontmatter `id`, never the filename.

**Pages.** Every rendered directory needs a `0_index.md`. Frontmatter stays compact: `id`, `title`, `nav_title`, `summary`, `status`, optionally `estimated_time`, `tags`, `prerequisites`, `aliases`.

> **Quote any frontmatter value containing a colon.** `summary: Datalake, warehouse: dos respuestas` is invalid YAML and fails the whole course build. This has already broken this repo once.

**Links.** Cross-page links use wikilinks `[[id]]` / `[[id|label]]` or `raya:<id>`. An ambiguous or missing wikilink fails validation. `prerequisites` must also name real stable IDs.

**Raw HTML is disabled.** The renderer runs `MarkdownIt("commonmark", {"html": False})`. No `<iframe>`, `<div>`, `<details>`, `<br>`. There is no PDF-embed directive — the deck in `2_pipeline_de_datos/6_presentacion.md` is offered as open + download links, not embedded.

**`@name` is a numbered-object reference.** Writing a bare `@itam.mx` in prose fails the build. Wrap literal at-signs in a code span: `` `@itam.mx` ``.

**Figures.** Images that need a number go in a directive block, numbered per page hierarchy by `render.numbered_objects` in `raya.yaml`:

```markdown
::: figure {#dag title="El pipeline como grafo de dependencias"}
![Diagrama de un pipeline como DAG](_assets/d-dag.svg)
:::
```

A bare `![]()` renders without a "Figura N" caption. Numbered-object IDs (figure, table, definition, problem) are unique **course-wide**, not per page — the builder keeps one set of seen IDs across every page, so a reused ID fails the build with `Duplicate numbered object ID`. Prefix them per unit (`rx-`, `git-`).

**Official learning objects.** YAML under `_official/<family>/`. Valid families: `assignments`, `cards`, `exams`, `examples`, `projects`, `prompts`, `quizzes`, `tasks`. Objects colocated beside a quantum omit `scope.quantum` (it is inferred); objects under source-root `course/_official/` **must** declare it. All IDs share one course-global namespace, including derived calendar occurrence IDs.

**Support directories don't render.** `_official/`, `_assets/`, `_reviewed/`, `_drafts/`, `_partials/`. Rendered Markdown may link into its own or an ancestor `_assets/`, never the others.

## The calendar

`course/_official/calendar/1_2026-o26.yaml` is a calendar document — a separate family from official learning objects, excluded from `data/official.json`.

Sessions run **Tuesday and Thursday, 19:00–20:30**, from 2026-08-11 to 2026-12-01. `calesc2026.pdf` at the repo root is the ITAM academic calendar those dates come from.

**The session list is incremental on purpose.** The calendar used to carry all 32 sessions pre-titled through December; the plan drifted far enough from that outline that the future entries were removed. Only sessions whose content actually exists are listed — currently `session-01` through `session-07`, ending at 2026-09-01 — plus one `cancellation` (Thu 2026-09-17, ITAM descanso obligatorio) and three `milestone` entries. **Add the next `session-NN` when you author the unit it teaches, not before.** Keep the numbering and the Tue/Thu 19:00–20:30 slot; an empty future is the intended state, not a gap to fill with placeholders.

**Do not hand-write assignment dates as calendar events.** Every official object with `content.due` or `content.available` contributes its own occurrence automatically. Write the `assignment` once; the calendar derives it.

Every listed session carries a `page` reference: `el-curso`, `pipeline-de-datos`, `arquitectura-de-computadoras`, `software-libre-y-sistemas-operativos`, `terminal-directa`, `bash-scripting` and `expresiones-regulares`. A `page` that does not resolve to a rendered stable ID fails validation, so leave it off until the target page exists.

## Images

Two generators, both in `tools/`, both with the generator as the source of truth:

```bash
python3 tools/gen_diagramas.py                                  # los 8 SVG conceptuales
set -a && . ./.env && set +a                                    # carga OPENAI_API_KEY
python3 tools/gen_ilustraciones.py portada viaje etl-elt        # ilustraciones gpt-image-2
python3 -m pytest tools/ -q                                     # las guardas
```

Consequences worth internalizing:

- **Editing a generated SVG by hand fails `test_diagramas.py`.** Change the entry in `DIAGRAMAS` and rerun the generator.
- **Every image needs a row in `_assets/CREDITOS.md`** or `test_creditos.py` fails; crediting a file that does not exist fails too.
- **Illustrations are non-deterministic** and are never regenerated in CI. Generate once, review by eye, commit.
- Illustration prompts must never request real people or protected characters — `test_ilustraciones.py` enforces this.

## CI

`.github/workflows/pages.yml` runs `pytest tools/` as job `checks`, then calls the reusable workflow, which validates, builds, inspects, and deploys. `needs: checks` is what makes the tests a real gate — without it both jobs race and the site publishes even when the suite fails.

Deployment requires the repository to stay **public**: GitHub Pages is not available for private repos on this organization's plan.

## Content conventions

- Course language is Spanish; identifiers in English.
- Prose is dense and argumentative — introduce a concept as the answer to a concrete failure, not as a standalone definition. Read `course/2_pipeline_de_datos/4_cuando_se_rompe.md` for the register.
- Don't reuse third-party captures. Diagrams are regenerated as own-work SVG.
- Cite dated claims with their year. The "60 % of time cleaning data" figure is a ~2016 CrowdFlower survey and is labeled as recycled industry folklore, not fresh fact.
