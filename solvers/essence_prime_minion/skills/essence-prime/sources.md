# Sources for `essence-prime`

Tested with Savile Row 1.11.1 (bundled Minion), OpenJDK 17, Python 3.10, Ubuntu 22.04 (container).

Refactored from the DCP-Bench integration skill; examples verified with Savile Row 1.11.1.
The integration-specific rules that skill carried (how a benchmark runner binds instance
fields, enumerates and reports) now live in the integration's contract, not here.

Existing skills: none found for Essence' / Savile Row when the integration skill was written.

- Savile Row 1.11.1, 17 Oct 2025, Linux tarball
  <https://www-users.york.ac.uk/peter.nightingale/savilerow/savilerow-1.11.1-linux.tgz>,
  SHA-256 `7b9653bb9ffa8fd71b29f3d5c2de41011cdc136ed2241f82b39f86aa9b3489c6`. Its bundled
  `savilerow-manual.pdf` and sources gave the command line (4.5), solution and info file
  formats (4.3, 4.4), parameter files (2.2), globals (Table 1), objective and branching
  (2.4, 2.5) and the `-timelimit` / `-solver-options` semantics (4.5.9, 4.5.10). `savilerow -help`
  gave `-solutions-to-stdout`, `-params`, `-S0`/`-S1`, `-param-to-json` and `-mode ReadSolution`.
- Release notes <https://www-users.york.ac.uk/peter.nightingale/savilerow/releases.html> - version
  and bundled solvers (Minion, Chuffed, Kissat).
- Nightingale, "Savile Row Manual", arXiv:2201.03472 (version 1.10.1) - section numbers cited
  in `references/language.md` (2.1 expressions, 2.1.9 division, 2.1.16 quantifiers, 2.1.19
  table, 2.2 declarations, 2.3 where, App. B precedence).
- Nightingale and Rendl, "Essence' Description", arXiv:1601.02865 - cross-check of the language.
- `solvers/essence_prime_minion/run.py` and `readiness_test.py` in the DCP-Bench Open repository -
  the integration's submission contract (now in `solvers/essence_prime_minion/CONTRACT.md`);
  the padding-plus-row-length treatment of ragged data in the JSON example follows it.
- `rosetta-skills/model-generator/references/acceptance.md` (DCP-Bench Open) - the comment
  convention kept in Modelling rules (problem line, statement-worded comment per block).
- Lessons in Modelling rules, Pitfalls and Search and performance come from the campaign runs
  of this integration (Essence' models checked by its evaluator).
- <https://agentskills.io/specification> - the Agent Skills format.

Verified by running (Savile Row 1.11.1 in a container, 2026-10-13 and 2026-10-16):
- every example in `assets/` with the command in its README (`check_assets.py`), and the Quick start;
- decision-variable indexing, `|x|`, `gcc`, `table`, `exists`, `heuristic sdf`, the unsatisfiable
  `queens 3` info file, the `sum ... <= c` parse error;
- `-S1` (default) versus `-S0`: `find x : int(1..3)` with only `x != 2` gives 1 solution under
  `-all-solutions` and 2 with `-S0`; an unconstrained extra `find` is pinned under `-S1` and
  multiplies solutions under `-S0`;
- `-solver-options "-cpulimit 3"` on a Golomb ruler with 11 marks: a solution of length 74
  written with `SolverTimeOut:1`; `-timelimit 2` alone let Minion run for 100 s to the optimum;
- reserved names: `find min/max/table` and the keywords fail to parse, the names listed as
  accepted in `references/language.md` parse;
- `-all-solutions` on an optimisation model: warning, one best solution.
- an empty matrix (`letting edges = []` for `int(1..0)`): exit 0, the solution, and the two warnings on stderr;
  `savilerow` not on `PATH` in the image: `not found`, and `/opt/savilerow/savilerow` runs by full path;
  the job-shop example (`assets/jobshop`), the optimum 11 checked by brute force over machine orders;
  a single-variable objective fixed in pass 2 (`total = 6`) enumerates the 3 optimal knapsack selections.
Everything else in `references/language.md` comes from the manual and was not executed.
Independent toy test: 18/18
