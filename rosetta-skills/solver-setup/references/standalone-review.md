# Standalone review

A solver skill must work for anyone, outside this repository. `python -m generation.skills
rosetta-mentions <skill>` catches names (DCP-Bench, image tags, repository paths). This
review catches what names cannot: a skill that teaches this benchmark's way of submitting
a model instead of the solver's own way of using it. A release needs a clean review
(`python -m generation.release publish ... --review FILE`).

## Running it

Give a **fresh agent** that has not worked on the skill only two things: the skill folder
and this file. Not the integration's `CONTRACT.md`, `run.py` or the old skill: a reviewer
who knows the harness reads it into the text. Without a fresh agent, review it yourself
and say so in `reviewer`.

First get the digest of exactly the content that will be released. It covers git-tracked
files only, as a release does, so `git add` new files first (the command warns about any
untracked file it leaves out):

```bash
python -m generation.release digest <solver_id>     # prints "<skill> sha256:..."; the review names the sha256
```

## What counts as a leak

Read every file except `sources.md` and `evals/` (the release check
`python -m generation.skills rosetta-mentions` scans those for project names). Report a
line when it only makes sense for someone submitting a model to a benchmark runner:

| Category | Examples |
|---|---|
| `harness` | A model written as a function or predicate that something else calls (`build(instance)` returning a model and an outputs dictionary, `model/4` for a driver, `Build(json, builder, outputs)`), instead of a program that solves and prints |
| `runner` | Statements about "the runner", "the evaluator", "the driver", "the harness": what it proves, forces, enumerates, rejects or reports |
| `protocol` | Output dictionaries keyed by declared names for someone else to read, JSONL solution records, status strings such as `limit`, `complete`, `execution_error`, `invalid_output` |
| `benchmark` | Advice that only fits the benchmark: checking every instance, instance counts, declared outputs, references, hardcoded-answer warnings |
| `environment` | Facts about one particular container or test setup presented as the solver's: image names, `/opt/...` paths in that image, "inside the image" |

Not a leak: the solver's own API, its statuses and parameters, reading a data file in a
program the user runs, enumeration done by the user's own loop, timings measured
anywhere, generic installation advice (containers, `PATH`, no network), and the
readability rule from the add-solver template (a comment stating the problem, and a
comment in the problem statement's words before each block of constraints).

## Output

Write one JSON object to a file outside the skill folder (anything inside would change
the digest):

```json
{
  "skill": "<skill name>",
  "source_digest": "<the digest printed above>",
  "reviewer": "<who reviewed: agent and model, or 'self'>",
  "verdict": "standalone",
  "findings": []
}
```

`verdict` is `standalone` only when `findings` is empty; otherwise it is `leaks` and each
finding is `{"file": "SKILL.md", "line": 42, "quote": "<the text>", "category": "<one of
the categories>", "why": "<one sentence>"}`. Fix the skill, take a new digest, and review
again: a review covers exactly the digest it names.
