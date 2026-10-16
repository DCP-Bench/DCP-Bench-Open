# Sources for `maxicp-java`

Tested with MaxiCP 0.0.3 (`org.maxicp:maxicp`, Maven Central, jar sha256 `904df52a…90d6`), Java 21
(Eclipse Temurin 21, Ubuntu noble, Linux x86_64) and Gson 2.11.0.

Existing skills: none found. `npx skills find maxicp` could not run (the CLI needs Node 22); a GitHub code
search for `maxicp` in `SKILL.md` files returned nothing.

- <https://github.com/aia-uclouvain/maxicp> at tag `v0.0.3`, MIT licence (`README.md`): the raw and modelling
  API overview, and the raw N-queens example.
- Same tag, `src/main/java/org/maxicp/cp/CPFactory.java`, `search/DFSearch.java`,
  `search/AbstractSearchMethod.java`, `search/Searches.java`, `cp/engine/core/MaxiCP.java`: the factories,
  the search loop, the limit and completion semantics, the bugs in the `Searches` heuristics, and
  `makeIntervalVar(cp, len)` being optional. Read from the sources jar on Maven Central.
- Same tag, `userguide/source/learning_maxicp/getting_started.rst` and `search_strategies.rst`: the raw API
  walk-through and the `firstFailBinary`, `selectMin` and `optimize` usage.
- Same tag, `src/main/java/org/maxicp/cp/examples/raw/JobShop.java`: `makeIntervalVar(cp, false, len)` for
  tasks that must run.

Verified by running (Java 21 image, MaxiCP 0.0.3):

- `firstFailBinary` finds 92 solutions for 8-queens; `firstFailNary` returns one unfixed "solution";
  `heuristicNary(minDomVariableSelector(q))` finds 13 for 8-queens and never branches on the largest value.
- `optimize` with a stopping predicate reports `isCompleted() == false`; without one, the last optimum is
  reported with `isCompleted() == true`.
- Enumerating all optima: `optimize`, then `eq(obj, optimum)` at the root, then no-goods, gives the six
  optima of the 3-machine min-makespan example.
- `makeIntVar(cp, 3, 1)` throws `InvalidParameterException: at least one setValue in the domain`.
- A bound of `Integer.MAX_VALUE` is refused with a message naming the int limits.
- An objective that is not fixed at a solution throws `objective not bound`.
- `cp.post` of a constraint refuted at the root throws `InconsistencyException`.
- The examples' expected outputs, the inline Quick start (copied from this file) and the examples' runs with
  only `maxicp-0.0.3.jar` on `CLASSPATH`.
