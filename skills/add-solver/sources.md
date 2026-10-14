# Sources for `add-solver`

- https://agentskills.io/skill-creation/best-practices — only what the agent lacks, defaults over menus, gotchas, validation loops
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices — name/description limits, references one level deep, Contents list over 100 lines, fresh-instance testing
- https://github.com/vercel-labs/skills — `npx skills find`, `npx skills add <repo> --list`, searched directories
- https://github.com/tiangolo/library-skills — skills in Python wheels, `uvx library-skills`
- https://github.com/agentskills/agentskills/tree/main/skills-ref — reference validator. It is not on PyPI ("demonstration purposes only"), so it is installed from git. Verified: it validates this skill and rejects a bad name and a folder-name mismatch, through both `uvx` and the venv fallback
- CPMpy `skills/cpmpy-explain` — style of the generated-skill template (tables, Contents, Common issues, Further reading)
- DCP-Bench Open `solvers/pysat/skills/pysat` — claims verified by running, `sources.md`
- [NVIDIA/cuopt](https://github.com/NVIDIA/cuopt) `skills/` and [NVIDIA/skills](https://github.com/NVIDIA/skills) — runnable `assets/<example>/` with a README per example (tested in CI by `ci/test_skills_assets.sh`), evals with `expected_skill` and negative cases; see `docs/nvidia-skills-report.md` in the experiments repo

Toy problems: `jobshop/small` from the [OR-Tools job-shop example](https://developers.google.com/optimization/scheduling/job_shop), `jobshop/ft06` from [JSPLIB](https://github.com/tamy0612/JSPLIB) (optimum 55), and `knapsack/p01` from [FSU KNAPSACK_01](https://people.sc.fsu.edu/~jburkardt/datasets/knapsack_01/knapsack_01.html) (optimum 309). `knapsack-all-optimal` instances were constructed (`fourteen` drawn at random) and their counts confirmed by exhaustive enumeration; `name`/`note` keys were added to some instances to test that loaders ignore extra fields.

Verified by running: all answer keys were confirmed with CPMpy 1.1.1 / OR-Tools 9.15, whose reference models pass `run_toy_tests.py` 15/15; the `knapsack-all-optimal` keys by a brute-force enumeration and an OR-Tools CP-SAT model (3/3), and the original 15 OR-Tools models still pass after the `name`/`note` keys were added. The checkers reject infeasible, suboptimal, duplicate, incomplete and malformed output.
