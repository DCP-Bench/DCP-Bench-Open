---
name: choco-java
description: Choco 6.0.1, a constraint solver for Java with integer and Boolean variables, global constraints (all different, cumulative, table, circuit, regular and more), search strategies, restarts and lazy clause generation, for finding, enumerating or optimising solutions. Use when writing, debugging or explaining Choco models in Java, or when the user has chosen Choco for a constraint or scheduling problem.
license: Apache-2.0
compatibility: Requires a JDK (tested with Java 21, single-file launch needs JDK 11+), the choco-solver 6.0.1 jar-with-dependencies (Maven Central, BSD-3-Clause) and, for JSON input, Gson 2.11.0 (Apache-2.0). No key or size limits.
metadata:
  domain: constraint-programming
  solver: choco
  paradigm: cp
---

# Choco 6.0.1 (Java)

Choco is a propagation-based constraint solver written in Java, with a large catalogue of global
constraints. A model is an `org.chocosolver.solver.Model`, which is also the factory for every
variable and constraint. A factory call returns a `Constraint` that does nothing until you call
`.post()` (or reify it). **Model with the globals.** Choco's strength is its propagators: a
decomposition into pairwise `arithm` or reified sums throws that away.

Docs: [Choco documentation](https://choco-solver.org/docs/) (modelling, search, solving).

## Contents
- [Install](#install) · [Quick start](#quick-start) · [Modelling](#modelling) · [Solving](#solving)
- [All solutions](#all-solutions) · [All optimal solutions](#all-optimal-solutions) · [Optimisation](#optimisation)
- [Common issues](#common-issues) · [Runnable examples](#runnable-examples) · [Further reading](#further-reading)
- References: [constraints.md](references/constraints.md) (every factory method, grouped),
  [catalogue.java](references/catalogue.java) (each global checked against brute force, with and without LCG),
  [examples.md](references/examples.md) (two longer models: shift roster, machines with a crew), [sources.md](sources.md)

## Install

```bash
mkdir -p lib
curl -fsSLo lib/choco-solver-6.0.1-jar-with-dependencies.jar https://repo1.maven.org/maven2/org/choco-solver/choco-solver/6.0.1/choco-solver-6.0.1-jar-with-dependencies.jar
curl -fsSLo lib/gson-2.11.0.jar https://repo1.maven.org/maven2/com/google/code/gson/gson/2.11.0/gson-2.11.0.jar
export CLASSPATH="$PWD/lib/choco-solver-6.0.1-jar-with-dependencies.jar:$PWD/lib/gson-2.11.0.jar"
java -version
```

The examples run as single files with `java File.java`, which reads `CLASSPATH`. Only the JSON
examples need Gson: Choco has no JSON reader. Choco logs SLF4J warnings on stderr; they are harmless.
Details and downloads: [Choco documentation](https://choco-solver.org/docs/), Maven artifact
[choco-solver 6.0.1](https://repo1.maven.org/maven2/org/choco-solver/choco-solver/6.0.1/). To compile
a class with a `main` method instead: `javac -cp "$CLASSPATH" Main.java && java -cp "$CLASSPATH:." Main`.

## Quick start

```java
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;

// Place 8 queens on a chessboard so that no two share a row, a column or a diagonal.
public class Queens {
    public static void main(String[] args) {
        int n = 8;
        Model m = new Model("queens");
        IntVar[] q = m.intVarArray("q", n, 0, n - 1);   // q[i] = row of the queen in column i
        IntVar[] up = new IntVar[n], down = new IntVar[n];
        for (int i = 0; i < n; i++) {
            up[i] = m.offset(q[i], i);      // q[i] + i: one value per up-diagonal
            down[i] = m.offset(q[i], -i);   // q[i] - i: one value per down-diagonal
        }
        m.allDifferent(q, "AC").post();          // no two in the same row
        m.allDifferent(up, "AC_REGIN").post();   // no two on the same up-diagonal
        m.allDifferent(down, "AC_REGIN").post(); // no two on the same down-diagonal
        if (m.getSolver().solve()) {
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < n; i++) sb.append(q[i].getValue()).append(i < n - 1 ? " " : "");
            System.out.println("rows by column: " + sb);
        } else System.out.println("no solution");
    }
}
```

Run with `java Queens.java`; it prints `rows by column: 0 6 3 5 7 1 4 2`. The views on the diagonals
need `"AC_REGIN"` or `"BC"` (see [Common issues](#common-issues)).

## Modelling

Write the model clause by clause, finding the row here for each sentence of the description. `m` is the
`Model`. Arrays are `IntVar[]`, and constants are `int[]`. Semantics in brackets are verified in
[catalogue.java](references/catalogue.java); every method in [constraints.md](references/constraints.md).

| The description says | Post |
|---|---|
| all different | `m.allDifferent(x, "AC").post()` (`"BC"` for wide domains) |
| all different after shifts (queens diagonals) | `m.allDifferent(views, "AC_REGIN").post()`, `views[i] = m.offset(q[i], i)` (not `"AC"` or the default over views: see Common issues) |
| all different except 0 / except values | `m.allDifferentExcept0(x)`, `m.allDifferentExceptValues(x, vals...)` |
| exactly k equal to v | `m.count(v, x, k)` [k = #{x_i = v}]; v or k may be an `IntVar` |
| how many take a value in a set | `m.among(k, x, int[] values)` |
| value v_j occurs c_j times (gcc) | `m.globalCardinality(x, int[] values, IntVar[] occ, closed)` [closed: every x_i in values] |
| number of distinct values | `m.nValues(x, k)`; bounds: `atMostNValues`, `atLeastNValues` |
| how many are true / weighted sum | `m.sum(bools, "<=", k)`, `m.scalar(x, int[] w, "<=", cap)` [Σ w_i·x_i ≤ cap] |
| the i-th value of a table / array | `m.element(y, int[] table, i)` [y = table[i]], `m.element(y, int[] t, i, 1)` [1-based], `m.element(y, IntVar[] xs, i, 0)` |
| a cell of a matrix indexed by variables | `m.element(z, int[][] a, row, 0, col, 0)` posts at once; **bound `col` yourself** [it indexes the flattening] |
| allowed combinations / compatibility table | `Tuples t = new Tuples(true); t.add(...); m.table(x, t).post()`; forbidden: `new Tuples(false)` |
| a pattern along a sequence (shifts, nonogram row) | `m.regular(x, new FiniteAutomaton("(0\|1)*2{1,2}0")).post()` [one digit per symbol, `<12>` for 12] |
| a sequence with a cost per position | `m.costRegular(x, cost, CostAutomaton.makeSingleResource(fa, costs, lo, hi))` |
| visit every node once and return (tour) | `m.circuit(succ).post()` [succ_i = next node, 0-based], `m.circuit(succ, 1)` for 1-based |
| tour with optional nodes | `m.subCircuit(succ, 0, length)` [skipped nodes have succ_i = i] |
| Hamiltonian path from s to e | `m.path(succ, s, e)` [succ has domain 0..n; **succ[e] = n**] |
| a forest / tree over parents | `m.tree(parent, nbTrees)` [roots have parent_i = i] |
| one task at a time on a machine | `m.cumulative(tasks, ones, m.intVar(1))`; optional: `m.taskVar(s, d, BoolVar performed)` |
| resource capacity over time | `m.cumulative(starts, int[] dur, int[] use, cap)` or the `Task[]` form with `IntVar` heights |
| items into bins with capacities | `m.binPacking(bin, int[] size, load, 0)` [load_j = Σ size_i over bin_i = j]; bound `load` |
| choose quantities under weight, maximise value | `m.knapsack(occ, weightSum, valueSum, int[] w, int[] v)` |
| rectangles do not overlap | `m.diffN(x, y, w, h, true)` (sizes as `m.intVar(c)`) |
| a sorted copy / order statistics | `m.sort(x, y)`; by key columns: `m.keySort(rows, perm, sorted, k)` |
| a permutation and its inverse (position ↔ item) | `m.inverseChanneling(x, y)` [x_i = j ⇔ y_j = i]; offsets: `(x, y, ox, oy)` |
| a value as one-hot Booleans | `m.boolsIntChanneling(b, v, offset)` [exactly one b_i = 1, v ∈ offset..offset+n−1] |
| interchangeable values (colours, groups, machines) | `m.intValuePrecedeChain(x, new int[]{0, 1, .., k})` |
| interchangeable rows | `m.lexChainLessEq(rows)`, two rows: `m.lexLessEq(a, b)` |
| increasing / nondecreasing sequence | `m.increasing(x, 1)` / `m.increasing(x, 0)` |
| minimum / maximum / position of the maximum | `m.min(y, x)`, `m.max(y, x)`, `m.argmax(i, 0, x)` [first index on ties] |
| a set (team, group, subset) | `SetVar s = m.setVar(new int[]{}, universe)`, `s.getCard()`, `m.disjoint`, `m.partition`; outputs through `m.setBoolsChanneling(b, s)` |
| arithmetic | `m.times(x, y, z)`, `m.div` [truncates], `m.mod` [sign of x], `m.absolute(y, x)`, `m.square(y, x)` [y = x²], `m.pow(x, k, y)`, or expressions: `x.mul(y).add(z).eq(5).post()` |
| x differs from y plus a constant | `m.arithm(x, "-", y, "!=", c)`, or `x.sub(y).ne(c).post()` |
| logic between conditions | `x.gt(1).imp(y.eq(0)).post()`, `.and`, `.or`, `.xor`, `.iff`, `.not()`; `m.ifThen(c1, c2)` posts at once |
| if-then-else value | `z.eq(b.eq(1).ift(x, y)).post()` (`ift` is on a relational expression) |
| a condition as a 0/1 value | `BoolVar b = m.arithm(x, "<", y).reify()`, or `x.lt(y).boolVar()` |

A decomposition is the right choice only when no row fits. Two globals on the same variables are fine (an
`allDifferent` beside a `sum`), and redundant globals often pay: `globalCardinality` occurrences
that sum to n, or a crew `cumulative` beside per-machine ones.

**Readable models.** Open the program with a `//` comment stating the problem, and start each constraint
block with a `//` comment in the description's words, not the Choco call.

**Imports** (each checked in [catalogue.java](references/catalogue.java)):

```java
import org.chocosolver.solver.Model;
import org.chocosolver.solver.Solver;
import org.chocosolver.solver.SettingsBuilder;
import org.chocosolver.solver.constraints.Constraint;
import org.chocosolver.solver.constraints.extension.Tuples;
import org.chocosolver.solver.constraints.nary.automata.FA.FiniteAutomaton;
import org.chocosolver.solver.constraints.nary.automata.FA.CostAutomaton;
import org.chocosolver.solver.constraints.nary.cnf.LogOp;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.search.limits.FailCounter;
import org.chocosolver.solver.search.strategy.selectors.variables.FirstFail;
import org.chocosolver.solver.search.strategy.selectors.values.IntDomainMin;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import org.chocosolver.solver.variables.SetVar;
import org.chocosolver.solver.variables.Task;
import java.util.OptionalInt;
```

### Variables and data

- `m.intVar("x", lo, hi)` is an enumerated domain, `m.intVar("x", lo, hi, true)` is bounds only (use it for sums,
  times, objectives and anything wide), and `m.intVar("x", new int[]{1, 3, 7})` takes listed values.
  - Constants: `m.intVar(5)`.
  - Arrays: `m.intVarArray("x", n, lo, hi)`, matrices: `m.intVarMatrix("x", rows, cols, lo, hi)`, giving `IntVar[rows][cols]`.
- `BoolVar` extends `IntVar`: a `BoolVar[]` goes wherever an `IntVar[]` is expected, and
  `m.sum(bools, ...)` uses the Boolean sum.
- Views cost no propagator: `m.offset(x, c)`, `m.mul(x, a)`, `m.neg(x)`, `m.abs(x)`,
  `m.isEq(x, v)`, `m.isLeq(x, v)`, and `b.not()`.
- Bounds must fit in a Java `int`. When a product of two domains can overflow an `int`, `times`
  switches to a slower propagator, and under LCG it throws. Give intermediate variables tight bounds
  from the data. A number beyond the `int` range has to be written as digit variables (one `IntVar` in
  0..9 per decimal digit, most significant first) and printed from its digits.
- A column of a matrix is a new array: `IntVar[] col = new IntVar[rows]; for (...) col[r] = x[r][c];`.
- Tight domains from the data. A result variable made by a factory takes its bounds from its
  inputs: `m.sum("total", x)`, `m.max("mx", x)`, `m.element("v", table, i)`, `e.intVar()`.
- Take every size (item count, group count, days, the length of a list) from the input data, never from a
  number copied out of one example.

### Expressions and reification

- Arithmetic expressions on any IntVar:
  - `add`, `sub`, `mul` (an int, an expression, or several), `div`, `mod`, `abs`, `sqr`, `pow`, `neg`, `dist`, `min` and `max`.
  - Comparisons give relational expressions: `eq`, `ne`, `lt`, `le`, `gt`, `ge`, `in(...)` and `notin(...)`.
  - Relational expressions combine with `and`, `or`, `xor`, `imp`, `iff`, `not` and `ift`.
- What to do with an expression:
  - `r.post()` posts it.
  - `e.intVar()` and `r.boolVar()` turn it into a variable.
  - `r.extension()` turns a small expression into a table, which is often stronger than its decomposition.
- **Relations are not numbers.** `x.eq(1).add(...)` does not compile. Sum `boolVar()`s, or use
  `count`/`among`.
- `c.reify()` gives a BoolVar equal to c, and `c.reifyWith(b)` reifies with a given BoolVar.
  `c.implies(b)` is c ⇒ b and `c.impliedBy(b)` is b ⇒ c.
- `m.ifThen`, `m.ifThenElse`, `m.ifOnlyIf` and the `reifyX..` methods post at once. Do not call `.post()` on them, since they return void.
- `m.and(...)`, `m.or(...)` and `m.not(c)` return a Constraint to post. `m.not` is generic and weak on globals.

## Solving

Call `solve()` on the solver, `Solver s = m.getSolver()`. It returns `true` at the next solution and `false`
when the search is exhausted. **Read the values inside the loop.** After the `false`, the search has
backtracked, so `getValue()` on a variable read after the loop throws `is not instantiated`. Keep the
best values in local variables as the loop runs (see the examples).

- **Limits:** `s.limitTime("10s")`, `limitFail`, `limitSolution`. `s.reset()` returns to the root and removes
  the limits. Constraints may be posted after a reset (not under LCG).
- **Search state:** `s.getSearchState()` is `SearchState.TERMINATED` when the search was exhausted and
  `STOPPED` when a limit was hit (`org.chocosolver.solver.search.SearchState`).
- **Strategies:** `m.getSolver().setSearch(s1, s2, ...)` runs the strategies in order. Branch first on the few
  variables that decide the structure. A search that must label every variable can extend a strategy over
  all of them with `makeCompleteStrategy(true)`.
  - `Search.inputOrderLBSearch(x)` follows array order, smallest value first, and `inputOrderUBSearch` takes the largest first.
  - `Search.minDomLBSearch(x)` is first-fail.
  - Learning heuristics: `Search.domOverWDegSearch(x)`, `activityBasedSearch`, `conflictHistorySearch`, `failureRateBasedSearch`. Pair them with restarts.
  - These take one `IntVar...` list. Join several arrays first: `ArrayUtils.append(a, b)` (`org.chocosolver.util.tools.ArrayUtils`).
  - Custom: `Search.intVarSearch(new FirstFail(m), new IntDomainMiddle(true), x)`. Value selectors also include `IntDomainMin`, `IntDomainMax`, `IntDomainMedian`, `IntDomainRandom(seed)` and `IntDomainBest`.
  - Wrappers: `Search.lastConflict(s)` and `Search.bestBound(s)`.
  - Scheduling: `m.setTimes(tasks)`.
- **Restarts:** `solver.setLubyRestart(50, new FailCounter(m, 1), 10000)` or `setGeometricalRestart(10, 1.2, new FailCounter(m, 1), 10000)`.
  Add `setNoGoodRecordingFromRestarts()` to keep learnt no-goods.
- With no strategy set, Choco picks a black-box default (`Search.defaultSearch(m)`). It is good on
  many models.
- A grid puzzle encoded with placement Booleans (a ship, a piece, a word at each position):
  branch on the cell variables first, then on the placements. Branching on the placements
  alone timed out where cells first solved in seconds.
- Scheduling: branch on start times smallest first (`inputOrderLBSearch(starts)` or
  `setTimes`). Routing: branch on successors with first-fail.
- Optimisation that finds a poor first solution and stalls: build good solutions first. Choices
  with a cost from a table: `cost_i = m.element("c", costRow_i, choice_i)`, then branch on the `cost_i`
  with `minDomLBSearch` so the cheapest choice comes first.
- On a timeout, first switch the search style: in-order without restarts against dom/wdeg
  with Luby restarts. Then add implied constraints, such as a lower bound on the objective
  (total demand / capacity, rounded up) or per-row partial sums. Implied constraints usually beat a
  change of heuristic.

### Lazy clause generation (LCG)

`new Model("m", SettingsBuilder.init().setLCG(true))` learns clauses from conflicts, and it can win
large on scheduling and on models with weak propagation. In 6.0.1 it is not safe for every
constraint.

- **Wrong answers:** `m.not(allDifferent)` counted 0 solutions instead of 21.
- **Exceptions:** `distance`, `sort`, `tree`, `regular`, every set constraint, and the SAT `addClauses*`
  layer throw.
- **Checked under LCG:** the arithmetic, sums, count/among/gcc/nValues, element, allDifferent, table, circuit/subCircuit/path, cumulative,
  diffN, binPacking, knapsack, lex, precedence, channelling and the expression API.
- **Optimisation:** under LCG, Choco restarts the search after every solution.
- **Rebuild, do not reset:** under LCG, constraints cannot be posted after a reset, so build the model again
  in a method for every new search (see [All solutions](#all-solutions)).

Turn LCG on only for a model whose constraints are all on the checked list, and compare its answer with a run without LCG.
The LCG example, [lcg-machine](assets/lcg-machine/README.md), does this.

## All solutions

`while (solver.solve())` returns every distinct assignment of **every** variable in the model, auxiliary
ones included: a free `aux` in 0..5 with `x` in 1..2 gives 12 solutions, and with `aux = x` it gives 2.
Make each auxiliary a function of the outputs (fix it with a constraint such as a total), so that it cannot
repeat a solution: [all-solutions-coins](assets/all-solutions-coins/README.md) does this with its amount.

When an auxiliary cannot be fixed that way, keep the solutions distinct on the outputs with a **no-good**
after each solution: reset the solver, then post "some output differs from its value in this solution",
and continue the loop:

```java
Solver s = m.getSolver();
int count = 0;
while (s.solve()) {
    count++;
    int vx = x.getValue(), vy = y.getValue();     // the outputs of this solution
    s.reset();                                     // back to the root; limits are removed
    m.or(m.arithm(x, "!=", vx), m.arithm(y, "!=", vy)).post();   // no-good on the outputs
}
```

On the model `x <= y` with `x, y` in 0..2 and `z = x + y` the loop counts 6. Under LCG, constraints cannot
be posted after a reset: rebuild the model in a method, post the no-goods on the fresh model, and solve again.

## All optimal solutions

Optimise first, then enumerate every choice with the optimum. The optimising loop reports only strictly
better solutions, so an equal-cost choice never appears there. Instead:

1. Run the optimising loop and check `TERMINATED` (see [Optimisation](#optimisation)); keep the optimum.
2. Build the model again in a method, post `cost == optimum`, and loop `solve()` over it, reading the outputs.

[all-optimal-pair](assets/all-optimal-pair/README.md) does exactly this: a `build()` method returns the
model and its variables, and the second model posts `arithm(total, "=", best)`.

## Optimisation

- The objective must be an **IntVar**: `m.setObjective(Model.MINIMIZE, v)` or `Model.MAXIMIZE`, once,
  on an IntVar with bounds wide enough for every attainable value (derive them from the data).
  Make the objective from an expression with `m.sum("total", x)` or `m.scalar(x, w, "=", total)`, which
  creates the IntVar and posts the equality.
- Each `solve()` that returns `true` in an optimisation is strictly better than the one before.
- **The last solution is optimal only if `getSearchState()` is `TERMINATED`, not `STOPPED`.**
  A `STOPPED` search has a feasible best, not a proof. Report "not proven optimal" then.
- Do not bound the objective with a value the model does not imply (an expected or remembered best). The
  cut silently removes solutions, and the proof then covers the constraint rather than the model.
- Examples: [maximise-production](assets/maximise-production/README.md) (maximise),
  [minimise-transport](assets/minimise-transport/README.md) (minimise), [scheduling-project](assets/scheduling-project/README.md)
  (makespan through `m.max`), [json-knapsack](assets/json-knapsack/README.md) (maximise, data from JSON).

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| A constraint is silently ignored (`m.allDifferent(x);` alone) | Not `.post()`ed. The void methods (`ifThen`, `ifThenElse`, `ifOnlyIf`, `reifyX..`, 2D `element`, the `*Dec` decompositions and `addClauses*`) post themselves | Add `.post()`, or reify on purpose |
| `java.lang.Error: This element is not present in the in-list` | `allDifferent(views, "AC")`, or the default consistency, over views (`m.offset`, `m.mul`, `m.neg`): a Choco 6.0.1 bug, reproduced on Langford-style positions | Over views use `"AC_REGIN"` or `"BC"`, or post the shifted values as their own IntVars. Plain variables are not affected |
| `new Tuples(int[][], boolean)` does not compile | Not in 6.0.1 | `new Tuples(true)` then `t.add(int[]...)`. For a universal ("any") value: `new Tuples(tuples, true, OptionalInt.of(star))`; `setUniversalValue` called afterwards does nothing; an algorithm ending in `+` rejects forbidden tuples |
| 2D `element(z, int[][] a, row, 0, col, 0)` reads across into the next row | `col` runs past the row length, since it indexes the flattening | Bound `col` yourself |
| `path` or `circuit` fails at once | Wrong domain | `circuit` over n nodes: domain 0..n−1 (plus the offset); `path`: `succ[e] = n`, not a node |
| `boolsIntChanneling` cannot express "none" | It forces exactly one Boolean true | Give "none" its own index |
| `distance(x, y, op, c)` throws | Only `"="`, `"!="`, `"<"` and `">"` are accepted | `distance(x, y, ">", 1)` for at least 2 apart, or `x.dist(y).ge(2).post()` |
| `div` or `mod` results look wrong for negatives | `div` truncates toward 0; `mod` takes the sign of the dividend, as in Java | Expect Java's behaviour |
| `ift` does not compile on a Boolean | `ift` exists only on relational expressions | Write `b.eq(1).ift(x, y)`, not `b.ift(x, y)` |
| `globalCardinality(..., closed = true)` makes the model infeasible or strange | `closed` forces every variable into the listed values | List every value the variables may take, or use `closed = false` |
| `m.max` or `m.count` compile error or wrong result | Argument order: `max(IntVar max, IntVar[] vars)` takes the result first; `count(v, x, n)` takes the value first | Fix the order |
| `realVar` fails | Real variables need Ibex, which is not in the jar used here | Scale to integers |
| Compile errors about `Model` or `Solver` | A class of your own named `Model` hides `org.chocosolver.solver.Model` | Rename the class |
| `times` is slow, or LCG throws "Multiplication constraint is not supported in LCG mode" | A product of two domains can overflow an `int` | Give intermediate variables tight bounds from the data |
| `x.eq(1).add(...)` does not compile | Relations are not numbers | Sum `boolVar()`s, or use `count`/`among` |
| Optimisation ignores the objective | The objective is not an IntVar | Post `scalar`/`sum` onto a fresh IntVar and pass it to `setObjective` |
| The last optimisation solution is reported as optimal after a limit | `STOPPED`, not `TERMINATED` | Check `getSearchState() == TERMINATED` before calling it optimal |
| `getValue()` throws `is not instantiated` after the loop | The search backtracked when `solve()` returned `false` | Keep the values in locals inside the loop |
| Duplicate solutions in an enumeration | An auxiliary variable is free | Make it a function of the outputs, or no-good on the outputs ([All solutions](#all-solutions)) |
| Constraints posted after a reset fail or are ignored under LCG | Posting after a reset is not allowed under LCG | Build the model again in a method |
| LCG gives a wrong count (`not(allDifferent)` counted 0 instead of 21) | The constraint is not safe under LCG | Turn LCG off, or use only checked constraints ([LCG](#lazy-clause-generation-lcg)) |
| LCG throws on `distance`, `sort`, `tree`, `regular`, a set constraint, or `addClauses*` | Not supported under LCG | Use a different encoding, or turn LCG off |
| `java.lang.OutOfMemoryError` at posting or during search | A very wide enumerated domain, a table with too many tuples, or an `allDifferent` / `element` over large domains | Use bounds (`true`) for wide ranges, tighter bounds from the data, smaller tables, and decompose less; a bigger heap only hides the cause |
| Slow, or no first solution / optimum not proven | Weak propagation or branching | Global instead of decomposition, `"AC"` where a stronger one fits, implied constraints, a better search, restarts ([Solving](#solving)) |
| JSON boolean read as 0 or 1 fails | Gson's `getAsInt()` throws on a JSON boolean | `getAsBoolean() ? 1 : 0` ([json-knapsack](assets/json-knapsack/Knapsack.java)) |
| JSON rows have different lengths and the model reads past the end | Ragged lists | Take each row's length with `size()` on that row |
| A Java class does not run, or stdout is noisy | SLF4J warnings on stderr | Harmless; read stdout only |

## Runnable examples

Each folder is a standalone program: `java File.java` from inside it, with `CLASSPATH` set as in
[Install](#install). `json-knapsack` takes `data.json` as argument.

| Pattern | Folder |
|---|---|
| satisfy, `allDifferent` on rows, columns and boxes | [satisfy-sudoku](assets/satisfy-sudoku/README.md) |
| all solutions, functional auxiliary | [all-solutions-coins](assets/all-solutions-coins/README.md) |
| all optimal solutions | [all-optimal-pair](assets/all-optimal-pair/README.md) |
| maximise | [maximise-production](assets/maximise-production/README.md), [json-knapsack](assets/json-knapsack/README.md) (data from JSON with Gson) |
| minimise, grid of flows | [minimise-transport](assets/minimise-transport/README.md) |
| infeasible | [infeasible-pigeonhole](assets/infeasible-pigeonhole/README.md) |
| scheduling, `cumulative`, makespan | [scheduling-project](assets/scheduling-project/README.md) |
| lazy clause generation on a checked model | [lcg-machine](assets/lcg-machine/README.md) |

Two longer models, with their data inline, are in [examples.md](references/examples.md).

## Further reading

- Choco documentation (modelling, search strategies, restarts, solving): <https://choco-solver.org/docs/>
- Choco source and releases: <https://github.com/chocoteam/choco-solver> (tag [v6.0.1](https://github.com/chocoteam/choco-solver/releases/tag/v6.0.1))
- Maven artifact: <https://repo1.maven.org/maven2/org/choco-solver/choco-solver/6.0.1/>
