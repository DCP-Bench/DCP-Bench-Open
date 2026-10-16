# Sources for `essence-prime`

- Savile Row 1.11.1, 17 Oct 2025, Linux tarball
  <https://www-users.york.ac.uk/peter.nightingale/savilerow/savilerow-1.11.1-linux.tgz>,
  SHA-256 `7b9653bb9ffa8fd71b29f3d5c2de41011cdc136ed2241f82b39f86aa9b3489c6`. Its bundled
  `savilerow-manual.pdf` and sources gave the command line (4.5), solution and info file
  formats (4.3, 4.4), parameter files (2.2), globals (Table 1), objective and branching
  (2.4, 2.5) and the `-timelimit` / `-solver-options` semantics (4.5.9, 4.5.10).
- Release notes <https://www-users.york.ac.uk/peter.nightingale/savilerow/releases.html> - version
  and bundled solvers (Minion, Chuffed, Kissat).
- Nightingale, "Savile Row Manual", arXiv:2201.03472 (version 1.10.1) - section numbers cited
  in the notes behind `references/language.md` (2.1 expressions, 2.1.9 division, 2.1.16
  quantifiers, 2.1.19 table, 2.2 declarations, 2.3 where, App. B precedence).
- Nightingale and Rendl, "Essence' Description", arXiv:1601.02865 - cross-check of the language.
- `solvers/essence_prime_minion/run.py` and `readiness_test.py` in this repository - the
  submission contract: `given` binding of instance fields, padding and `_len` fields, one matrix
  per column for mixed rows, refusals, optimum-before-emit and the fixed-objective enumeration.
- `rosetta-skills/model-generator/references/acceptance.md` - the comment requirement.
- <https://agentskills.io/specification> - the Agent Skills format.

Run in the `dcp-eval/essence_prime_minion:v1` image on 2026-10-13: the models in
`references/examples.md` (standalone with `/opt/savilerow/savilerow`, and through
`evaluation.evaluate`), a model using decision-variable indexing, `|x|`, `gcc`, `table`,
`exists`, `heuristic sdf`, the unsatisfiable `queens 3` output, the `sum ... <= c` parse error, and
that a `given` without an instance field fails. Everything else in `references/language.md`
comes from the manual and was not executed.
