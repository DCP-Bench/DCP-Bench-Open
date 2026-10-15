# Solver skill template

Layout:

```
<name>/
  SKILL.md               entry point
  assets/<example>/      one runnable example per folder: the program + README.md
  references/            only when needed (per-interface API detail, cheatsheet)
  sources.md
  evals/evals.json
```

No empty folders or placeholder files.

**Examples are files, not Markdown.** Each worked example (beyond the Quick start) is a complete program in `assets/<example>/` — e.g. `assets/knapsack/model.py` — so it can be run and re-run when the solver changes. Its `README.md` follows this shape, which `scripts/check_assets.py` executes:

```markdown
# Knapsack (maximise)

**Problem:** 0/1 knapsack with 3 items, capacity 7.
**Shows:** boolean variables, linear constraint, maximise, proven-optimal status check.
**Run:** `python model.py`
**Expected:** `Objective: 70`
```

`Run` is one shell command executed in the example folder (compile and run for compiled languages: `g++ -std=c++17 main.cpp -lchuffed -o main && ./main`). `Expected` (repeatable) is text that must appear in stdout. Pick examples that cover what the toy problems exercise — satisfy, all solutions, all optimal solutions, maximise, minimise, infeasible, scheduling — as small general patterns, not copies of the toy problems. **One example reads its data from a JSON file** whose path is the first command-line argument, with a bundled `data.json` as the default: it names the JSON library and how to install it (or shows a small reader when the language has none), takes every size from the data, handles a ragged list, and ignores keys it does not use. Prefer shortened versions of the solver's official examples, credited in `sources.md`.

Skeleton for `SKILL.md`. Adapt the sections to the solver, and drop any that do not apply.

**Link the docs where they are needed, not only at the end.** Each section opens or closes with its doc page (install guide, API page, status codes, parameters, enumeration feature), and table rows link to the API entry they name. Prefer `llms.txt`, `.md` or plain-HTML pages. *Further reading* keeps only the general entry points: agent docs, the full API reference and examples.

````markdown
---
name: <framework>-<language>
description: <What the solver or framework is: language, paradigm, package/import names.> Use when <writing, debugging or explaining models with it; typical problem words; the user has chosen this tool>.
license: <licence of the skill text, e.g. Apache-2.0>
compatibility: Requires <language/runtime version> and <package>; <licence or size limits, if any>
metadata:
  domain: constraint-programming
  solver: <solver>
  paradigm: <cp | sat | maxsat | smt | mip | asp | clp>
  related-skills: "<owner>/<repo>[, ...]"   # only if a complementary skill was found and not bundled
---

# <Solver> (<Language>)

<One paragraph: what kind of solver, and the one idea a modeller must keep in mind
("every constraint must be linear", "the program is grounded first").>

<Only if related-skills is set:>
> **Related skill:** `<skill-name>` (<what it adds>) is not included here. When <the situation it helps with>, suggest the user install it: `npx skills add <owner>/<repo>`.

## Contents
- [Install](#install)
- [Quick start](#quick-start)
- [Modelling](#modelling)
- [Solving](#solving)
- [All solutions](#all-solutions)
- [Common issues](#common-issues)
- [Further reading](#further-reading)
- <Runnable examples, one folder per pattern: [<example>](assets/<example>/README.md), …>

Links point at files, never at folders: `skills-ref` and the repository validator reject a link to a directory, so link an example's `README.md`.

## Install

```bash
<exact unpinned command(s)>
<one-line verification, e.g. python -c "import x; print(x.__version__)">
```

<Licence/edition limits, in one or two lines.> Details: [<install guide>](<URL>)

## Quick start

```<lang>
<smallest complete model: data, variables, constraints, objective, solve, print values, check status>
```

## Modelling

Full list: [<API reference / global constraint catalogue>](<URL>)

| Need | API |
|---|---|
| integer variable | [`<exact call>`](<URL to its API entry>) |
| all different | [`<exact call>`](<URL>) |
| element / table / cumulative / no-overlap | [`<exact call>`](<URL>) |
| reification / implication | [`<exact call>`](<URL>) |
| read data from a file (sizes from the data, extra keys ignored) | [`<exact call>`](<URL>) |
| minimise / maximise | [`<exact call>`](<URL>) |

<Short code blocks only for patterns a table cannot show.>

## Solving

Status values: [<status codes page>](<URL>) · Parameters: [<parameters page>](<URL>)

| Status | Meaning |
|---|---|
| `<OPTIMAL>` | <proven optimal> |
| `<FEASIBLE>` | <solution found, optimality not proven (e.g. timeout)> |
| `<INFEASIBLE>` | <proven no solution> |
| `<UNKNOWN>` | <limit hit, nothing found> |

<Reading values. Time limit / threads / seed parameter names.>

<Where errors appear (stderr, stdout, log file, verbose flag), and the solver's own solution checker if it has one.>

## All solutions

<The enumeration API, and how to avoid duplicates. All optimal solutions: solve, post `(objective) = optimum`, then enumerate over the output variables.> Details: [<enumeration / solution pool page>](<URL>)

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| <symptom an agent sees: error text or wrong result> | <cause> | <fix, or a link to the section that has it> |

## Further reading

- Documentation for agents: <llms-full.txt or .md docs URL>
- API reference: <URL>
- Examples: <URL> (<which files are worth reading>)
````

Rules for the content:
- **Description**: says *what* and *when*, in roughly 400 characters or fewer. It is not a list of what the skill covers.
- **Test material stays out.** The toy problems' output format, test results and sandbox quirks go in the report, not in the skill or in `sources.md`.

## sources.md

```markdown
# Sources for `<name>`

Tested with <solver> <version>, <language> <version>, <OS>.

Existing skills: <none found | each one: source / companion / ignored — one line on why>

- <URL> — <what was taken from it>
- Learned from <upstream skill URL> (<licence>, <version>) — <what it contributed>   ← only for a source skill

Verified by running: <claim> — <how>
```

## evals/evals.json

One entry per toy-problem family, plus 2–3 **negative** prompts where the skill should not activate (same problem with another solver named, a non-modelling task about the solver). `expected_skill` lets a benchmark score whether the right skill was picked:

```json
{"skill_name": "<name>", "evals": [
  {"id": 1, "prompt": "Solve this 0/1 knapsack with <solver> from <language> …", "expected_skill": "<name>",
   "expected_output": "Proven-optimal selection", "assertions": ["Uses <solver>'s maximise API", "Checks the status is proven optimal"]},
  {"id": 9, "prompt": "Write a MiniZinc model for n-queens.", "expected_skill": null,
   "expected_output": "The skill is not used", "assertions": ["<name> is not loaded"]}]}
```
