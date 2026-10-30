# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A **course source repository**, not an application. It holds authored Markdown/YAML for the ITAM course *Fuentes de Datos — Otoño 2026*, consumed by the Raya Lucaria framework (Glintstone static builder) to generate a static site published to GitHub Pages at **https://rayalucaria.org/fdd_o26/**.

The published site comes from `raya.yaml`, `course/`, `skins/`, and `.github/workflows/pages.yml`. `tools/` holds image generators plus the pytest guards that protect them; it never renders. Other top-level directories don't render either. `codigo/` holds the per-task starter templates students copy. `estudiantes/<login>/` is where student pull requests land. `.github/tareas/` holds the task fichas, and `docs/superpowers/plans/` holds dated design plans for past unit rewrites, which are useful history when you change a unit.

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

**Mistakes `raya validate` misses.** A few authoring errors pass validation, or break it in ways that are hard to trace. Each one has a guard in `tools/`, so run `pytest tools/` as well as `validate`:

- **Wikilink inside a table.** Write `[[id|label]]` with the pipe *unescaped*. The escaped form `[[id\|label]]` breaks the whole build with "Broken wikilink reference" (`test_wikilinks.py`).
- **Callouts.** Only a line that is exactly `> [!NOTE|TIP|WARNING|CAUTION]` becomes a callout. `[!IMPORTANT]` or trailing text prints literally, and nothing fails (`test_callouts.py`).
- **SVG root size.** Every SVG must declare `width`/`height` on its root. With only a `viewBox` it renders as a ~70 px thumbnail (`test_svg_tamano_intrinseco.py`).
- **Unit 2 (pipeline) only.** A term must be defined before any page uses it, and it must appear in `7_glosario` (`test_vocabulario.py`). Unit prose is capped at 9500 words (`test_presupuesto.py`). A diagram must draw the terms its page teaches (`test_diagramas_terminologia.py`).

## The calendar

`course/_official/calendar/1_2026-o26.yaml` is a calendar document — a separate family from official learning objects, excluded from `data/official.json`.

Sessions run **Tuesday and Thursday, 19:00–20:30**, from 2026-08-11 to 2026-12-01, with two exceptions, both **19:00–20:00**: `session-10` (Thu 2026-09-17), because the opening class of the containers unit is given without computers, and `session-13` (Thu 2026-10-01), the Python environments class. `course/0_index.md` and `README.md` both state the schedule and those two exceptions; the three move together. `calesc2026.pdf` at the repo root is the ITAM academic calendar those dates come from.

**The session list is incremental on purpose.** The calendar used to carry all 32 sessions pre-titled through December; the plan drifted far enough from that outline that the future entries were removed. Only sessions whose content actually exists are listed — currently `session-01` through `session-19`, ending at 2026-11-03 — plus one `cancellation` entry (Tue 2026-09-15, the only holiday that lands on a class day; the November holidays, 2 and 16, are Mondays and do not touch the course, so there is class on Tue 2026-11-03 and 2026-11-17) and four `milestone` entries. These dates come from `calesc2026.pdf`; verify against it before changing one. **Add the next `session-NN` when you author the unit it teaches, not before.** Keep the numbering and the Tue/Thu 19:00–20:30 slot (`session-10` and `session-13` are the two documented exceptions); an empty future is the intended state, not a gap to fill with placeholders.

**Do not hand-write assignment dates as calendar events.** Every official object with `content.due` or `content.available` contributes its own occurrence automatically. Write the `assignment` once; the calendar derives it.

Every listed session carries a `page` reference: `el-curso`, `pipeline-de-datos`, `arquitectura-de-computadoras`, `software-libre-y-sistemas-operativos`, `terminal-directa`, `bash-scripting`, `expresiones-regulares`, `seccion-git`, `seccion-github`, `la-idea-del-contenedor`, `contenedores-con-las-manos`, `disenar-con-contenedores`, `ambientes-python`, `python-por-dentro`, `elegir-el-stack`, `apis-y-http` and `computo-y-concurrencia`. A `page` that does not resolve to a rendered stable ID fails validation, so leave it off until the target page exists.

## The exams annex

`course/99_examenes/` is a review annex, not a unit. It has no session in the calendar. `1_parciales/` holds the in-class midterms, one subdirectory per exam with versions A and B and their answer-free PDFs in `_assets/`. `2_ejercicios_extra/` holds extra exercises in the same shape. Each question is a `::: problem {#id ...}` block followed by `::: answer {of="id"}`, which the renderer folds, so no raw HTML is needed. Problem IDs carry per-exam prefixes (`paa-`/`pab-`, `pta-`/`ptb-`, `pga-`/`pgb-`, `pda-`/`pdb-`, `xa-`, `xt-`, `xg-`, `xd-`, `xc-`) because of the course-wide ID rule above.

The printable sources live in top-level `examenes/`, which is **gitignored** (`examenes/*`) because the repo is public. That folder holds `.docx` files and the Node scripts that generate them (`NODE_PATH=<dir with node_modules/docx> node examenes/parciales/gen_control_docker.js`). Never commit anything from it. Only the course pages and the PDFs are published.

## Images

Diagrams come from one deterministic generator **per unit** in `tools/` (`gen_diagramas.py` for pipeline, `gen_regex.py`, `gen_git.py`, `gen_contenedores.py`, `gen_contenedores_bench.py`, `gen_python.py` (covers all sections of unit 9), `gen_ai_*` for the architecture unit's dashboards). Each one owns a `DIAGRAMAS` catalog that it shares with its tests as the single list of figures that exist: `test_gen_*.py` for most, `test_diagramas.py` + `test_diagramas_terminologia.py` for `gen_diagramas.py`, and `test_gen_contenedores.py` also covers `gen_contenedores_bench.py`. The palette lives once in `tools/svg_base.py`, mirrored from `skins/fdd-eva.yaml`. Import it from there and never repeat it. `tools/gen_notebook_por_dentro.py` generates the template notebook for 9.2; never edit it by hand. `tools/gen_notebook_apis.py` does the same for 10.1 (`codigo/10_apis/apis.ipynb`), and `tools/test_apis_curriculum.py` checks it byte for byte and starts `codigo/10_apis/servidor.py` to check that the server does what the pages show. Unit 11 (computo y concurrencia) has `tools/gen_computo.py` and `tools/gen_computo_b.py` (figures prefixed `cmp-`, into `course/11_computo_y_concurrencia/_assets/`) and `tools/gen_notebook_computo.py` (generates `codigo/11_computo/computo.ipynb` from `tools/notebook_computo/*.py`), checked by `tools/test_gen_computo.py`, `tools/test_gen_computo_b.py` and `tools/test_computo_curriculum.py`. The 9.3 notebooks (`codigo/09_python/stack/*.ipynb`) are the opposite: hand-written, denser than their pages, saved without outputs. Illustrations are the one non-deterministic generator:

```bash
python3 tools/gen_diagramas.py                                  # o gen_regex.py, gen_git.py, ...
set -a && . ./.env && set +a                                    # carga OPENAI_API_KEY
python3 tools/gen_ilustraciones.py portada viaje etl-elt        # ilustraciones gpt-image-2
python3 -m pytest tools/ -q                                     # las guardas
python3 -m pytest tools/test_gen_git.py::test_name -q           # una sola
```

A few tests (`test_diagramas.py`, `test_ai_dashboard_*`) build the course with Raya and **skip** unless they find it. They look for `raya_lucaria/.worktrees/navigation-first-course-rail` among the repo's ancestors, or for `RAYA_CHECKOUT`. A green local run without that checkout has not exercised them (see `tools/raya_test_support.py`).

Consequences worth internalizing:

- **Editing a generated SVG by hand fails its generator's test.** Change the entry in that generator's `DIAGRAMAS` and rerun it.
- **Every image needs a row in `_assets/CREDITOS.md`** or `test_creditos.py` fails; crediting a file that does not exist fails too.
- **Illustrations are non-deterministic** and are never regenerated in CI. Generate once, review by eye, commit.
- Illustration prompts must never request real people or protected characters — `test_ilustraciones.py` enforces this.

## CI

`.github/workflows/pages.yml` runs `pytest tools/` as job `checks`, then calls the reusable workflow, which validates, builds, inspects, and deploys. `needs: checks` is what makes the tests a real gate — without it both jobs race and the site publishes even when the suite fails. It runs on fork PRs too, on purpose: the useful work there is `raya validate`, which catches a broken course before the merge. The reusable workflow already gates the deploy itself to a push on the default branch, so nothing publishes from a PR.

`.github/workflows/entregas.yml` is the student-submission gate, and `.github/scripts/revisa_entrega.py` holds its logic. Six blocking rules: every touched file lives under `estudiantes/<PR author's login>/`, that folder name matches the login exactly (case included), no garbage was **added** (deletions are ignored on purpose — removing a stray `.DS_Store` is the right move), the PR does not come from the fork's default branch, the branch name matches `tarea-NN-nombre` (checked only when the PR isn't already coming from the default branch, since that rule reports first), and every touched file under the student's folder lives in a **single** subfolder — a loose file at the folder's root (a `.gitkeep`) doesn't count, a pure deletion doesn't count either, but a rename between two subfolders fails because it touches both, and when the branch is in the workflow's task map (env var `TAREAS`) that one folder must also be the one the branch owns. The default-branch rule has a grace period: `BRANCH_ESTRICTA_DESDE` in the workflow is the date it starts blocking instead of warning — it exists because the group already had PRs open from `main` when the rule landed. The branch-name rule has its own, separate grace period, `BRANCH_NOMBRE_ESTRICTO_DESDE`: a different variable on purpose, because no task had ever told a student what to name their branch, unlike the default-branch policy, which was already in force and which nobody asked to relax. Deleting either variable makes its rule strict immediately; it never disables it. The one-folder rule carries **no** grace period — it blocks from day one. Accounts listed in the workflow's `MANTENEDORES` env var are exempt, and bots are skipped entirely.

**The trigger is `pull_request_target`, and it must stay that way.** With `pull_request` GitHub runs the workflow *and the script* from the PR's merge ref, so a student could rewrite `revisa_entrega.py` in their own PR and approve themselves. The price of `pull_request_target` is that this job must never execute PR code: the checkout is pinned to `base.sha` with `persist-credentials: false`, and the script only queries the API — it never reads the working tree. `tools/test_revisa_entrega.py` asserts both of those structurally (note: PyYAML parses the `on:` key as the boolean `True`, not `"on"`).

One subtlety worth keeping: a rename reports only the destination in `filename`, so the script also validates `previous_filename` — otherwise `git mv course/x estudiantes/me/x` passes green and the merge deletes the course file. (The `/files` endpoint also caps at 3000, so the script compares its count against the PR's `changed_files` and fails closed on a mismatch.) It deliberately does **not** chase `..` or absolute paths: Git rejects those in the index already.

The content that promises these checks lives in two places, `course/7_git_y_github/2_github/4_el_flujo_del_curso.md` and `estudiantes/README.md`, so all three — script, workflow, and those two pages — move together; this repo already let one of them drift out of sync once. The mirror rule is **not** machine-checked — say so wherever it is described.

Two details of the grace periods: both dates are compared against the PR's **opening** date (`created_at`), not today — otherwise a PR opened inside the grace turns red the moment the student pushes a fix. And when what failed is the branch itself (default branch or bad name), the closing message says the delivery goes in a **new** branch, the one exception to "push to the same branch".

### Per-task CI: the ficha (from 2026-09-22 on)

`entregas.yml` has a **third** step, `.github/scripts/revisa_ficha.py`, that runs the checks declared in `.github/tareas/<branch>.toml` — the task's **ficha** (schema in `.github/tareas/README.md`). No ficha for a branch means nothing to check (green, silent). The ficha is read from disk, which is safe **only** because the checkout is pinned to `base.sha`; the script reads nothing but `.github/tareas/` and `codigo/` from disk (a test spies `open` to prove it) and the student's files only through the API. Its messages say **what** is wrong, **why**, and **where to investigate** — never how to fix it (the teacher's rule). Prompt-injection text in a student file is reported as a warning, never obeyed.

- **Old deliveries keep their rules.** `tarea-08-datacamp-intro` and `tarea-08-imagen` stay in the `CATALOGO` inside `revisa_contenido.py`, and that catalog no longer grows (a test pins it). Every new task gets a ficha.
- **Creating a task:** use the `crear_tarea` skill (ficha + official YAML + template in `codigo/` + `TAREAS` entry + board row + tests + adversarial pass).
- **Reviewing deliveries:** use the `revisar_tarea` skill (it replaced `review_class_pr`): all-or-nothing verdict with teacher override, comparison between deliveries (`compara.py`), slop/incoherence signals stated as verifiable facts — never "copied" or "used AI".
- **The review registry** lives on the orphan branch `registro-entregas` (`registro.csv`, one row per delivery attempt, **GitHub login only**, never real names). It is kept out of `main` on purpose because the repo is public; never merge that branch. Write to it with `.claude/skills/revisar_tarea/registro.py`.
- The boards `course/8_contenedores/7_D_entregas.md`, `course/9_python/1_ambientes/12_B_entregas.md`, `course/9_python/2_por_dentro/6_A_entregas.md` (delivery `tarea-09-por-dentro`), `course/9_python/3_stack/5_A_entregas.md` (delivery `tarea-09-stack`) and `course/11_computo_y_concurrencia/B_entregas.md` (delivery `tarea-11-datacamp-fastapi`; its Antigravity notice has no delivery) also describe what the automatic review checks, so they move together with the scripts, the fichas and the two pages above.

Deployment requires the repository to stay **public**: GitHub Pages is not available for private repos on this organization's plan.

## Content conventions

- **Students work only inside their own folder.** Every lab, exercise and task is done in `estudiantes/<login>/`, copied from `codigo/` with the mirror rule, after opening their fork in VS Code and updating `main` — never in a folder outside the repo (`~/lab-*`, `~/fdd/docker-lab`). That keeps their work versioned, in one place, and reviewable. Creating the folder is the student's job; pages give the commands. Labs travel in the PR of the task that shares their **subfolder** (e.g. `09_python/ambientes/` goes with `tarea-09-uv-docker`, `09_python/por_dentro/` with `tarea-09-por-dentro`, and `09_python/stack/` with `tarea-09-stack`). Generated environments (`.venv/`) stay out of git through `.gitignore` and the `BASURA` list. Unit 8 predates this rule and still uses `~/fdd/docker-lab`. Section 10.1 (`10_apis/`) has no task: students work it on a `clase-10-apis` branch that never becomes a PR (`11_computo/` likewise, on `clase-11-computo`), so their `main` keeps fast-forwarding. `tools/test_python_curriculum.py` enforces it for unit 9, `tools/test_python_por_dentro.py` enforces section 9.2, and `tools/test_python_stack.py` enforces section 9.3.
- Course language is Spanish; identifiers in English.
- Commits follow the history's Conventional Commit shape scoped by unit or area: `feat(unidad-3): ...`, `fix(entregas): ...`, `docs(skills): ...`. `AGENTS.md` carries a shorter version of these rules for other agents, so keep the two consistent.
- Prose is dense and argumentative — introduce a concept as the answer to a concrete failure, not as a standalone definition. Read `course/2_pipeline_de_datos/4_cuando_se_rompe.md` for the register.
- Don't reuse third-party captures. Diagrams are regenerated as own-work SVG.
- Cite dated claims with their year. The "60 % of time cleaning data" figure is a ~2016 CrowdFlower survey and is labeled as recycled industry folklore, not fresh fact.
