# Sources for `choco-java`

- Choco 6.0.1 (2026-05-21) from Maven Central:
  `org.choco-solver:choco-solver:6.0.1`, the `jar-with-dependencies` artifact, sha256
  `c1956f7688f0982c55dc12edfa5695b60085fb9c37f3fbc6cf7efc53afc0da39`. Upstream:
  <https://github.com/chocoteam/choco-solver/releases/tag/v6.0.1>. Licence: BSD-3-Clause.
- `choco-solver-6.0.1-sources.jar` from the same Maven directory: every signature in
  `references/constraints.md` was extracted from the factory interfaces `Model` implements
  (`IIntConstraintFactory`, `ISchedulingFactory`, `IReificationFactory`, `ISatFactory`,
  `IDecompositionFactory`, `IResultVariableFactory`, `IVariableFactory`, `IViewFactory`,
  `ISetConstraintFactory`, `IGraphConstraintFactory`), plus `Solver`, `Search`, `Tuples`,
  `FiniteAutomaton`, `ArExpression` and `ReExpression`.
- Choco documentation, <https://choco-solver.org/docs/>: modelling, search strategies,
  restarts, solving.
- `references/catalogue.java` checks the semantics stated in SKILL.md and constraints.md against
  brute force in the image, once with default settings and once with LCG on. Its
  `signatures()` method compiles every other call these files name.
- The DCP section describes `solvers/choco_java/java/dcp/` (`Main`, `Instance`, `Outputs`) and
  `run.py`. The examples, and the seating model in SKILL.md, ran through that driver in
  `dcp-eval/choco_java:v1`.
