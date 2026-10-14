# Sources for `pycsp3-ace`

Documentation this skill's instructions were written from. Add an entry
whenever a claim here comes from a specific page or version.

- <https://pypi.org/project/pycsp3/2.6.1/>: pycsp3 2.6.1 wheel (sha256 06e86b0b8aaed3a2f72acf9d5cca32f0b7ef86a45fa0d30a2308871883dbf4d5), read from the extracted package: `__init__.py` (data binding, `solve`, `minimize`), `compiler.py` (`-data`, `-output`, one-key data), `solvers/solver.py` (result extraction, solver log), `solvers/ace/ace.py`
- <https://pycsp.org/>: PyCSP3 documentation, for the modelling API (`Var`, `VarArray`, `satisfy`, `minimize`, global constraints)
- <https://www.cril.univ-artois.fr/~lecoutre/ace/>: ACE solver, bundled as ACE-2.6.jar in pycsp3 2.6.1

Verified in the `pycsp3_ace` image (pycsp3 2.6.1, ACE-2.6, OpenJDK 17):

- `data.field` and `data["_field"]` access; a one-key instance and an instance
  with metadata strings both run.
- 2-D `VarArray(size=[2, 3], ...)` gives nested lists; `AllDifferent`, `Sum`,
  `Or` and element-wise comparisons solve.
- An output that no constraint mentions raises the explicit error described in
  the skill.
- A minimisation and a maximisation return the optimum and its solutions; an
  auxiliary variable that repeats output assignments is handled by the rounds.
- `solvers/pycsp3_ace/run.py` (the child runner, rounds, nogoods, optimum handling) and
  `evaluation/check.py` (reason names, `tolerate_inconclusive`, `INCONCLUSIVE`) in this repository.
  These describe the contract in `references/dcp-contract.md`.
- `generation/manage.py` (`evaluate`), read only, for the attempt-evaluation command.

Verified in the `dcp-eval/pycsp3_ace:v1` image on 2026-10-14. Each construct in
`references/language.md` and each code block in `SKILL.md` and `references/examples.md`
was run with one solve round on a three-variable instance; the two DCP models in
`references/dcp-contract.md` were run through `evaluation.check` (queens: 6 instances,
knapsack: 5 instances, all accepted). The failures listed as "Dropped" in `language.md` were
reproduced with the messages shown there. The harness is not committed.

Probed in `dcp-eval/pycsp3_ace:fixtest` (same runner as v1, plus the fixes in this skill's
revision): each XCSP keyword in `org/xcsp/common/Constants.class` (`KEYWORDS`), the reserved
identifiers, the 32-bit value limit and the domain-size limit in `references/language.md`. The
XCSP3 `SolutionChecker` class in `ACE-2.6.jar` (`org.xcsp.parser.callbacks`) checks each solution
against the instance; the runner uses it. ACE prints the cause of a Java failure only on its
stderr, which pycsp3 does not read; the image wraps ACE so that stderr reaches the log.
