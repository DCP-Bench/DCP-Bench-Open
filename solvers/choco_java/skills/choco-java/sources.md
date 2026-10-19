# Sources for `choco-java`

Tested with Choco 6.0.1 (2026-05-21) and Gson 2.11.0 on Eclipse Temurin JDK 21 (Linux container).

Existing skills: not searched in this refactor; an earlier version of this skill was written from the
Choco documentation and the jar's own sources.

- Choco 6.0.1 from Maven Central: `org.choco-solver:choco-solver:6.0.1`, the `jar-with-dependencies` artifact,
  sha256 `c1956f7688f0982c55dc12edfa5695b60085fb9c37f3fbc6cf7efc53afc0da39`. Upstream:
  <https://github.com/chocoteam/choco-solver/releases/tag/v6.0.1>. Licence: BSD-3-Clause.
- `choco-solver-6.0.1-sources.jar` from the same Maven directory: every signature in
  `references/constraints.md` was extracted from the factory interfaces `Model` implements
  (`IIntConstraintFactory`, `ISchedulingFactory`, `IReificationFactory`, `ISatFactory`,
  `IDecompositionFactory`, `IResultVariableFactory`, `IVariableFactory`, `IViewFactory`,
  `ISetConstraintFactory`, `IGraphConstraintFactory`), plus `Solver`, `Search`, `Tuples`,
  `FiniteAutomaton`, `ArExpression` and `ReExpression`.
- Gson 2.11.0 from Maven Central, <https://repo1.maven.org/maven2/com/google/code/gson/gson/2.11.0/gson-2.11.0.jar>,
  for the JSON examples. Licence: Apache-2.0. Checked: `getAsInt()` on a JSON boolean throws
  `NumberFormatException`; `getAsBoolean()` reads it.
- Choco documentation, <https://choco-solver.org/docs/>: modelling, search strategies,
  restarts, solving.
- `references/catalogue.java` checks the semantics stated in SKILL.md and constraints.md against
  brute force, once with default settings and once with LCG on. Its `signatures()` method compiles every
  other call these files name. All checks agreed with brute force on the tested run; the constraints that
  throw or miscount under LCG are the ones listed in SKILL.md.
- The examples under `assets/` run with `java File.java` and print the values listed in their READMEs.
  The optima were checked independently: the sudoku has one solution (checked by enumerating all
  completions of the grid); the transport cost 240, the production profit 17, the project makespan 8,
  the machine makespan 7 and the knapsack value 20 were checked by brute force; the choice of two items
  at cost 3 has two optima; the coin count 10 is the known number of ways.
- `references/examples.md`: the roster optimum 34 and the machine makespan 8 were run as written.
- The no-good recipe in SKILL.md was run: the loop on `x <= y` over 0..2 counts 6.
