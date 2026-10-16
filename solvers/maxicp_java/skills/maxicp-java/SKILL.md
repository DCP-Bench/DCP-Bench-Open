---
name: maxicp-java
description: MaxiCP 0.0.3, a constraint programming solver for Java from UCLouvain, used through its raw API (CPFactory, CPSolver, DFSearch) with integer and Boolean variables, global constraints, interval variables for scheduling, search, optimisation and solution enumeration. Use when writing, debugging or explaining MaxiCP models in Java, or when the user has chosen MaxiCP for a constraint or scheduling problem.
license: Apache-2.0
compatibility: Requires a JDK 21 (MaxiCP classes are compiled for release 21; tested with Eclipse Temurin 21), the MaxiCP 0.0.3 jar (MIT, Maven Central) and, for JSON input, Gson 2.11.0 (Apache-2.0). No key, account or size limits.
metadata:
  domain: constraint-programming
  solver: maxicp
  paradigm: cp
---

# MaxiCP 0.0.3 (Java)

MaxiCP is a CP solver: constraints are posted on a `CPSolver`, which propagates them to shrink variable
domains, and a `DFSearch` branches over variables until every one is fixed. **MaxiCP has no default
search and no default time limit.** The search does only what the branching function and the limit
predicate say. This skill covers the raw API (`org.maxicp.cp.CPFactory`, `CPSolver`, `DFSearch`); the
symbolic modelling layer (`org.maxicp.modeling`, `ModelDispatcher`) is a different API.

## Contents
- [Install](#install)
- [Quick start](#quick-start)
- [Modelling](#modelling)
- [Solving](#solving)
- [All solutions](#all-solutions)
- [Optimisation](#optimisation)
- [Common issues](#common-issues)
- [Runnable examples](#runnable-examples)
- [Further reading](#further-reading)

## Install

```bash
mkdir -p lib
curl -fsSLo lib/maxicp-0.0.3.jar https://repo1.maven.org/maven2/org/maxicp/maxicp/0.0.3/maxicp-0.0.3.jar
curl -fsSLo lib/gson-2.11.0.jar https://repo1.maven.org/maven2/com/google/code/gson/gson/2.11.0/gson-2.11.0.jar
export CLASSPATH="$PWD/lib/maxicp-0.0.3.jar:$PWD/lib/gson-2.11.0.jar"
java -version
```

The examples run as single files with `java File.java`, which reads `CLASSPATH`. Only the JSON example
needs Gson. The raw API needs nothing else. Details: [MaxiCP repository](https://github.com/aia-uclouvain/maxicp/tree/v0.0.3)
(tag `v0.0.3`), [Maven artifact](https://repo1.maven.org/maven2/org/maxicp/maxicp/0.0.3/).

## Quick start

```java
import org.maxicp.cp.engine.core.CPIntVar;
import org.maxicp.cp.engine.core.CPSolver;
import org.maxicp.search.DFSearch;
import org.maxicp.search.SearchStatistics;
import static org.maxicp.cp.CPFactory.*;
import static org.maxicp.search.Searches.*;

public class QuickStart {
    public static void main(String[] args) {
        CPSolver cp = makeSolver();
        CPIntVar x = makeIntVar(cp, 0, 2);
        CPIntVar y = makeIntVar(cp, 0, 2);
        // x and y add up to 2
        cp.post(eq(sum(x, y), 2));
        DFSearch search = makeDfs(cp, firstFailBinary(x, y));
        search.onSolution(() -> System.out.println("x=" + x.min() + " y=" + y.min()));
        SearchStatistics stats = search.solve();
        System.out.println("solutions: " + stats.numberOfSolutions() + ", completed: " + stats.isCompleted());
    }
}
```

Output: three lines `x=... y=...`, then `solutions: 3, completed: true`.

## Modelling

Start each block of constraints with a comment line taken from the part of the problem description it
encodes, for example `// every row holds different values`. The examples below follow this rule.

Full list: [CPFactory](https://github.com/aia-uclouvain/maxicp/blob/v0.0.3/src/main/java/org/maxicp/cp/CPFactory.java)
(static factories and constraints; `import static org.maxicp.cp.CPFactory.*`).

| Need | API |
|---|---|
| integer variable in lo..hi | `makeIntVar(cp, lo, hi)`, `makeIntVarArray(cp, n, lo, hi)` |
| integer variables in 0..sz-1 | `makeIntVarArray(cp, n, sz)` (the two-value form is the domain size, not the upper bound) |
| Boolean variable | `makeBoolVar(cp)`, `makeBoolVarArray(cp, n)` (a `CPBoolVar` is a `CPIntVar` of 0..1) |
| all different | `allDifferent(xs)` |
| disequality | `neq(x, y)`, `neq(x, k)` |
| linear equality or bound | `sum(xs, k)`, `sum(xs, y)` (the sum equals the variable `y`), `eq(x, k)`, `eq(x, y)`, `le(x, k)`, `ge(x, k)`, `ge(x, y)` |
| views (no new constraint) | `sum(xs)`, `mul(x, k)`, `plus(x, k)`, `minus(x)` (-x), `minus(x, k)` (x - k), `max(xs)`, `minimum(xs)` |
| element and table | `element(int[], idx)`, `table(xs, rows)` |
| reification and logic | `isEq(x, k)`, `isLe(x, y)`, `not(b)`, `or(bs)`, `implies(b1, b2)` |
| interval (task) | `makeIntervalVar(cp, false, len)`, `start(t)`, `end(t)`, `startAfter(t, r)`, `endBeforeStart(a, b)` |
| no overlap and makespan | `noOverlap(ts)`, `makespan(ts)` |

- `cp.post(c)` posts a constraint and propagates. If it is refuted there and then, it throws
  `InconsistencyException`.
- A variable is fixed by the search only if the branching array covers it. Pass every variable a solution
  must fix to `firstFailBinary`.
- A view (`sum`, `mul`, `max`, `element`, ...) follows the variables it is built from. It is fixed when they are.
- Bounds may not be `Integer.MIN_VALUE` or `Integer.MAX_VALUE`. For a number that does not fit an int, use
  digits or a smaller scale.

## Solving

- A search is `DFSearch search = makeDfs(cp, branching)`. `branching` is a `Supplier<Runnable[]>` that
  returns `EMPTY` when it has nothing to branch on (a solution), or `branch(left, right)` otherwise.
- Use `firstFailBinary(vars...)`: it picks the unfixed variable with the smallest domain, posts `x = min`
  on the left and `x != min` on the right. This is the default heuristic in this skill.
- `search.solve()` explores the whole tree. `search.solve(stats -> ...)` stops when the predicate is true.
- `SearchStatistics`: `numberOfSolutions()`, `numberOfFailures()`, `numberOfNodes()`, `timeInMillis()`,
  `isCompleted()`. `isCompleted()` is true only when the tree was exhausted; a stopped search is not completed.

| Result | Meaning |
|---|---|
| solutions > 0, completed | every solution was enumerated |
| solutions = 0, completed | no solution (infeasible) |
| completed = false | the predicate stopped the search; nothing is known about the rest |

- **Time limit:** none is built in. Pass a predicate: `search.solve(s -> s.timeInMillis() > 10_000)`. It is
  checked when the search picks its next alternative, so one long propagation is not interrupted.
- **Read values inside `onSolution`.** `solve` returns with the state restored to the root, and every
  variable is unfixed again. `search.onSolution(() -> value = x.min())` is correct; reading `x` after
  `solve` is not.

## All solutions

`onSolution` runs once per solution. Auxiliary variables (any variable outside the outputs) multiply
the solutions: a free `spare` in 0..5 makes each `(x, y)` appear six times. Either fix every auxiliary
through a constraint, or forbid each output assignment with a no-good:

```java
int[] values = new int[n];                                  // inside the loop, values of the outputs
DFSearch search = makeDfs(cp, firstFailBinary(xs));
search.onSolution(() -> { for (int i = 0; i < n; i++) values[i] = xs[i].min(); });
SearchStatistics stats = search.solve(s -> s.numberOfSolutions() >= 1);
if (stats.numberOfSolutions() == 0) break;                  // no solution left
CPBoolVar[] differ = new CPBoolVar[n];
for (int i = 0; i < n; i++) differ[i] = not(isEq(xs[i], values[i]));
try { cp.post(or(differ)); } catch (InconsistencyException last) { break; }   // nothing left to forbid
```

Posting at the root, after `solve` returns, persists; posting inside a branch is undone on backtrack.
Each pass builds a new `makeDfs`. [Min-makespan](assets/min-makespan/README.md) shows the full loop.

## Optimisation

- `IntObjective o = cp.minimize(x)` or `cp.maximize(x)`, with `x` a `CPIntVar` (a view such as `sum(...)`
  or `max(...)` is fine).
- `SearchStatistics stats = search.optimize(o)` (or `optimize(o, limit)`). Each improving solution
  tightens the bound. The last value recorded in `onSolution` is optimal **only if `stats.isCompleted()`**;
  otherwise report "not proven". No solution and `isCompleted()` means infeasible.
- The objective must be fixed at every solution. If it is not, MaxiCP throws `objective not bound`: add the
  objective to the branching array.
- To enumerate every optimum: post `eq(x, optimum)` at the root after `optimize`, then run the no-good loop
  above over the outputs.
- Do not bound the objective with a value the model does not imply.
- Examples: [project-selection](assets/project-selection/README.md) (maximise),
  [min-makespan](assets/min-makespan/README.md) (minimise, all optimal),
  [single-machine](assets/single-machine/README.md) (makespan over intervals).

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| `firstFailNary(...)` gives one "solution" with variables unfixed | Bug in 0.0.3: it passes no variables to its selector | Use `firstFailBinary`; a branching that returns `EMPTY` early declares a solution |
| `heuristicNary` misses the largest domain value (8-queens: 13 solutions, not 92) | Bug in 0.0.3: its loop runs `v < max` | Use `firstFailBinary` |
| `objective not bound` | The objective is not fixed by the branching array | Add the objective variable to the array passed to `firstFailBinary` |
| Tasks ignored: `noOverlap` does nothing, `makespan` is 0 | `makeIntervalVar(cp, len)` is optional (presence unknown) | `makeIntervalVar(cp, false, len)` for a task that must run |
| `InvalidParameterException: at least one setValue in the domain` | Empty domain, `lo > hi` | Check the bounds |
| `InvalidParameterException ... MIN_VALUE and MAX_VALUE not allowed` | A bound at the int limit | Use tighter bounds from the data |
| `InconsistencyException` from `cp.post` | Refuted at the root, outside the search | Catch it where the post is outside a search; inside a branch the search handles it |
| Values read after `solve` are the root's | State is restored on return | Read values in `onSolution` |
| Outputs repeat with different auxiliaries | Auxiliaries are branched on | Fix them, or use the no-good loop |
| `solve` returns 0 solutions and `completed` is false | The predicate stopped the search (often a time limit) | Raise the limit; a non-completed search proves nothing |

## Runnable examples

| Example | Shows |
|---|---|
| [magic-square](assets/magic-square/README.md) | `allDifferent`, sums over rows, columns and diagonals, counting every solution, an infeasible order |
| [project-selection](assets/project-selection/README.md) | maximise, JSON data with ragged groups and unused keys |
| [min-makespan](assets/min-makespan/README.md) | minimise a `max` of loads, proof check, every optimal assignment with no-goods |
| [single-machine](assets/single-machine/README.md) | interval variables, `noOverlap`, precedences, release times, makespan |

## Further reading

- Source and examples at tag `v0.0.3`: [repository](https://github.com/aia-uclouvain/maxicp/tree/v0.0.3); raw
  examples in `src/main/java/org/maxicp/cp/examples/raw/` (`nqueens`, `JobShop.java`).
- User guide, search strategies and scheduling chapters: [maxicp.org](http://www.maxicp.org).
- API Javadoc: [javadoc.io](https://javadoc.io/doc/org.maxicp/maxicp/latest/org.maxicp/module-summary.html).
