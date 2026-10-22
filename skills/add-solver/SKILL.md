---
name: add-solver
description: Creates and tests an agent skill for a constraint or optimisation solver or modelling framework (CP, SAT, MaxSAT, SMT, MIP, ASP, CLP; e.g. Choco, Gurobi, JuMP, MiniZinc). Use when the user wants a skill for a solver or framework, or asks whether one exists.
license: Apache-2.0
compatibility: Requires Python 3.10+ (checkers use the standard library only), internet access, and the solver's own toolchain
metadata:
  domain: constraint-programming
---

# Add a solver skill

Produce one self-contained skill folder `<framework>-<language>/` (e.g. `choco-python`, `pumpkin-rust`; own-language systems keep their name: `minizinc`, `clingo`) that teaches a fresh agent to install the solver or modelling framework and model with it. Below, "solver" covers both. The skill is about that tool only; benchmarks and runners stay out.

## Workflow

| Step | Output |
|---|---|
| 0. Ask the user, in one message: **solver + language**, **where to write the skill**, **how thorough** | name, output folder, depth |
| 1. Search for existing skills | each one classified: source / companion / ignore |
| 2. Research, check the licence, install, run a hello-world | `research.md`, working install |
| 3. Write the skill; run `check_assets.py` and `skills-ref` | the skill folder |
| 4. *(thorough only)* Fresh agent on the toy problems; fix the skill until they pass | test table, `evals/evals.json` |
| 5. Report: path, depth, decision, tested version, test table, related skills, known gaps | `report.md` |

After each step, send the user a one-line progress note: done, next, rough time left. Don't wait for a reply.

**Interface.** Build exactly what the user named. A modelling framework (JuMP, MiniZinc, CPMpy, Pyomo) uses its default backend unless one is named. A solver gets its **own** API, the one its developers ship (Chuffed → C++, Pumpkin → Rust, Choco → Java/pychoco), unless the user names a combination ("Chuffed via MiniZinc"). With several native interfaces, ask, proposing the one its docs use most. A missing compiler is installed (ask before `sudo`) or reported; it never changes the interface.

**Depth.** *Thorough* (default, often an hour or more) runs everything. *Quick* skips step 4 and says "not tested by an independent agent" in `sources.md` and the report; step 4 can be run later. With no answer, go thorough. Whenever the user is unavailable, take your own proposal and say why in the report.

**Workspace.** Everything that is not the skill goes in a sibling folder, kept afterwards:

```
<name>-workspace/
  research.md           filled-in references/research.md
  probes/               install and API experiments
  round-N/models/       the test agent's programs, exactly as written
  round-N/results.txt   output of run_toy_tests.py
  report.md
```

## 1. Find an existing skill

| Where | How |
|---|---|
| skills.sh registry | `npx skills find <solver>`, also the package name (`pychoco`, `docplex`) |
| A repo's skills | `npx skills add <owner>/<repo> --list` |
| Solver's repo | `skills/`, `.agents/skills/`, `.claude/skills/`, root `SKILL.md`; `gh search code "filename:SKILL.md <solver>"` |
| Python wheel | after installing: `uvx library-skills` |
| Vendor collections | [NVIDIA/skills](https://github.com/NVIDIA/skills), [google/skills](https://github.com/google/skills) |
| Agent-friendly docs | `<docs-site>/llms.txt`, `llms-full.txt`: the best thing to link to |

You always write your own skill. Spot-check each find by running one of its examples, then classify it:

| Found skill | Role | What to do |
|---|---|---|
| Overlaps with yours (modelling with this solver) | **Source** | Verify its claims by running them, write your own text, credit it in `sources.md` (URL, version, licence) |
| Covers something else (docs navigation, deployment, tuning) | **Companion** | Recommend it: `metadata.related-skills: "<owner>/<repo>"`, a *Related skill* note under the intro, the install command in the report. Installing is the user's call |
| Stale, broken, or irrelevant | **Ignore** | Say why in the report |

Link to other skills; copying one makes it ours to maintain and needs its licence to allow it. An overlapping skill is a source, never a companion: two skills with the same triggers compete.

## 2. Research and install

Fill in [references/research.md](references/research.md) from **official** docs, API reference, examples and changelog. Closed issues ("wrong result", "objective ignored") are the best source of gotchas.

- **Licence**: needing a key, account or registration (full Gurobi, CPLEX, Xpress, Hexaly) → stop and ask. A free edition that installs without one (gurobipy's size-limited licence, CPLEX Community) is fine; put its limits in `compatibility` and *Common issues*.
- Install as the docs recommend, project-local where possible; ask before `sudo`. Record the tested version in `sources.md`; the skill stays unpinned.
- Done when you have run one tiny model of each kind (satisfy, enumerate all, all optimal, maximise, minimise, infeasible) and one broken on purpose, to see where errors appear.

## 3. Write the skill

Start from [references/skill-template.md](references/skill-template.md). Rules:

- **Only what an agent lacks**: exact API names, status semantics, gotchas. No CP/MIP theory.
- **One default per task**, alternatives only when they matter.
- **Tables over prose**, code over tables. Every snippet is run before it goes in.
- **Examples are runnable files** in `assets/<example>/`; only the Quick start lives inline. Check them with `python scripts/check_assets.py <skill-folder>`.
- **Link in place**: each section links its doc page, each table row its API entry.
- **One place per fact**: *Common issues* maps symptom → fix and links back.
- `SKILL.md` under ~200 lines; references one level deep.

Validate with [skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref), installed from git into a hidden environment:

```bash
uvx --from "git+https://github.com/agentskills/agentskills#subdirectory=skills-ref" skills-ref validate <skill-folder>   # a folder path; `.` fails the name check
```

Without uv, use a venv in `~/.cache/skills-ref/` and `pip install` the same URL.

## 4. Test on the toy problems

Seven problems, 18 instances ([README](assets/toy-problems/README.md)).

1. Spawn a **fresh subagent** given only the new skill, each `problem.md` and `instances/`. Task: *one program per problem in `<workspace>/round-N/models/`, taking the instance path as argument, printing solutions as in problem.md; report where the skill was missing, wrong or unclear*. Without subagents, do it yourself from the skill alone and report the test as not independent.
2. Check every instance:
   ```bash
   python scripts/run_toy_tests.py --cmd 'python <workspace>/round-N/models/{problem}.py {instance}' | tee <workspace>/round-N/results.txt   # adapt to the language; --problems a,b reruns a subset
   ```
3. On failure, the README's table says what the skill lacks. Fix the **skill**, add the test agent's mistake to its *Common issues*, and rerun with a new fresh agent in `round-N+1/`. Problems, answer keys and checkers stay as they are. After 3 failed rounds, show the user the failing instances, checker messages and what you tried, and ask whether to continue, accept the gap or stop (unavailable: stop and report).
4. Ship the skill that passed: any later edit needs another round.
5. Write `evals/evals.json` as in the template.
