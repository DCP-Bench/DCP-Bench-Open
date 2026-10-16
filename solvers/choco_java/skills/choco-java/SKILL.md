---
name: choco-java
description: Write Choco 6.0.1 constraint models in Java that use its global constraints (allDifferent, globalCardinality/count/among/nValues, element, table/regular/costRegular, circuit/subCircuit/path/tree, cumulative with optional tasks, diffN, binPacking, knapsack, lex, value precedence, channelling, sets) with the right search strategy, restarts and, where it is safe, lazy clause generation. Also covers DCP-Bench Open submissions for the choco_java integration (public class Submission, static build).
compatibility: Choco 6.0.1 (Maven Central choco-solver jar-with-dependencies), Java 21 (Temurin). DCP-Bench use needs the repository and the image dcp-eval/choco_java.
---

# Choco 6.0.1 models in Java

Choco is a propagation-based CP solver written in Java, with a large catalogue of global
constraints. A model is an `org.chocosolver.solver.Model`, which is also the factory for every
variable and constraint. A factory call returns a `Constraint` that does nothing until you call
`.post()` (or reify it).

**Model with the globals.** Choco's strength is its propagators: a decomposition into
pairwise `arithm` or reified sums throws that away.

Other files:
- [references/constraints.md](references/constraints.md): every factory method, grouped.
- [references/catalogue.java](references/catalogue.java): each global checked against brute force, with and without LCG, plus a compile check of every call named here.
- [references/examples.md](references/examples.md).
- [sources.md](sources.md).

## Constraint map: read the description, pick the global

Write the model clause by clause, finding the row here for each sentence of the description. `m` is the
`Model`. Arrays are `IntVar[]`, and constants are `int[]`. Semantics in brackets are verified in
`catalogue.java`.

| The description says | Post |
|---|---|
| all different | `m.allDifferent(x, "AC").post()` (`"BC"` for wide domains) |
| all different after shifts (queens diagonals) | `m.allDifferent(views).post()`, `views[i] = m.offset(q[i], i)` |
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

## Program shape

```java
import org.chocosolver.solver.Model;
import org.chocosolver.solver.Solver;
import org.chocosolver.solver.variables.IntVar;

Model m = new Model("queens");
int n = 8;
IntVar[] q = m.intVarArray("q", n, 0, n - 1);
IntVar[] up = new IntVar[n], down = new IntVar[n];
for (int i = 0; i < n; i++) { up[i] = m.offset(q[i], i); down[i] = m.offset(q[i], -i); }
// no two queens share a column or a diagonal
m.allDifferent(q, "AC").post();
m.allDifferent(up, "AC").post();
m.allDifferent(down, "AC").post();
Solver s = m.getSolver();
while (s.solve()) { /* read q[i].getValue() */ }
```

- **Optimisation:** call `m.setObjective(Model.MINIMIZE, cost)` (or `MAXIMIZE`) on an IntVar. Each `s.solve()` then
  returns a strictly better solution. The last one is optimal if `s.getSearchState()` is
  `SearchState.TERMINATED` and not `STOPPED`.
- **Limits:** `s.limitTime("10s")`, `limitFail`, `limitSolution`. `s.reset()` returns to the root and removes
  the limits. Constraints may be posted after a reset (not under LCG).
- **Imports** (each checked in `catalogue.java`):

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
- **Classpath:** `choco-solver-6.0.1-jar-with-dependencies.jar`. It logs SLF4J warnings to stderr, which are harmless.

## Variables, arrays, data

- `m.intVar("x", lo, hi)` is an enumerated domain, `m.intVar("x", lo, hi, true)` is bounds only (use it for sums,
  times, objectives and anything wide), and `m.intVar("x", new int[]{1, 3, 7})` takes listed values.
  - Constants: `m.intVar(5)`.
  - Arrays: `m.intVarArray("x", n, lo, hi)`, matrices: `m.intVarMatrix("x", rows, cols, lo, hi)`, giving `IntVar[rows][cols]`.
- `BoolVar` extends `IntVar`: a `BoolVar[]` goes wherever an `IntVar[]` is expected, and
  `m.sum(bools, ...)` uses the Boolean sum.
- Views cost no propagator: `m.offset(x, c)`, `m.mul(x, a)`, `m.neg(x)`, `m.abs(x)`,
  `m.isEq(x, v)`, `m.isLeq(x, v)`, and `b.not()`.
- Bounds must stay within ±21474836 (`Integer.MAX_VALUE / 100`). A product of large domains
  overflows that, so bound intermediate variables from the data.
- A column of a matrix is a new array: `IntVar[] col = new IntVar[rows]; for (...) col[r] = x[r][c];`.
- Tight domains from the data. A result variable made by a factory takes its bounds from its
  inputs: `m.sum("total", x)`, `m.max("mx", x)`, `m.element("v", table, i)`, `e.intVar()`.

## Expressions and reification

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

## Search

- `m.getSolver().setSearch(s1, s2, ...)` runs the strategies in order. Branch first on the few variables that
  decide the structure. The driver below extends any strategy over all variables.
- Strategies:
  - `Search.inputOrderLBSearch(x)` follows array order, smallest value first, and `inputOrderUBSearch` takes the largest first.
  - `Search.minDomLBSearch(x)` is first-fail.
  - Learning heuristics: `Search.domOverWDegSearch(x)`, `activityBasedSearch`, `conflictHistorySearch`, `failureRateBasedSearch`. Pair them with restarts.
  - Custom: `Search.intVarSearch(new FirstFail(m), new IntDomainMiddle(true), x)`. Value selectors also include `IntDomainMin`, `IntDomainMax`, `IntDomainMedian`, `IntDomainRandom(seed)` and `IntDomainBest`.
  - Wrappers: `Search.lastConflict(s)` and `Search.bestBound(s)`.
  - Scheduling: `m.setTimes(tasks)`.
- Restarts: `solver.setLubyRestart(50, new FailCounter(m, 1), 10000)` or `setGeometricalRestart(10, 1.2, new FailCounter(m, 1), 10000)`.
  Add `setNoGoodRecordingFromRestarts()` to keep learnt no-goods.
- With no strategy set, Choco picks a black-box default (`Search.defaultSearch(m)`). It is good on
  many models.
- Scheduling: branch on start times smallest first (`inputOrderLBSearch(starts)` or
  `setTimes`). Routing: branch on successors with first-fail.
- Optimisation that finds a poor first solution and stalls: build good solutions first. Choices
  with a cost from a table: `cost_i = m.element("c", costRow_i, choice_i)`, then branch on the `cost_i`
  with `minDomLBSearch` so the cheapest choice comes first.
- On a timeout, first switch the search style: in-order without restarts against dom/wdeg
  with Luby restarts. Then add implied constraints, such as a lower bound on the objective
  (total demand / capacity, rounded up) or per-row partial sums. Implied constraints usually beat a
  change of heuristic.

## Lazy clause generation (LCG)

`new Model("m", SettingsBuilder.init().setLCG(true))` learns clauses from conflicts, and it can win
large on scheduling and on models with weak propagation. In 6.0.1 it is not safe for every
constraint.

- **Wrong answers:** `m.not(allDifferent)` counted 0 solutions instead of 21.
- **Exceptions:** `distance`, `sort`, `tree`, `regular`, every set constraint, and the SAT `addClauses*`
  layer throw.
- **Checked under LCG:** the arithmetic, sums, count/among/gcc/nValues, element, allDifferent, table, circuit/subCircuit/path, cumulative,
  diffN, binPacking, knapsack, lex, precedence, channelling and the expression API.
- **Optimisation:** under LCG, Choco restarts the search after every solution.

Turn LCG on only for a model whose constraints are all on the checked list, and compare its answer with a run without LCG.

## Pitfalls

- A constraint that is not posted is silently ignored: `m.allDifferent(x);` without `.post()`.
  The exceptions are the void methods (`ifThen`, `ifThenElse`, `ifOnlyIf`, `reifyX..`, 2D `element`,
  the `*Dec` decompositions and `addClauses*`), which post themselves.
- `new Tuples(int[][], boolean)` does not exist in 6.0.1. Use `new Tuples(true)` and then
  `t.add(int[]...)`.
  - For a universal ("any") value use `new Tuples(tuples, true, OptionalInt.of(star))`.
  - `setUniversalValue` called afterwards does nothing.
  - An algorithm ending in `+` rejects forbidden tuples.
- 2D `element(z, int[][] a, row, 0, col, 0)` lets `col` run past the row length into the next
  row. Bound it.
- `path`: `succ[e] = n`, not a node. `circuit` over n nodes needs domain 0..n−1 (plus the offset).
- `boolsIntChanneling` forces exactly one Boolean true. For "none", give it its own index.
- `distance(x, y, op, int c)` accepts only `"="`, `"!="`, `"<"` and `">"`; it throws on `">="`. Write
  `distance(x, y, ">", 1)` for at least 2 apart, or use `x.dist(y).ge(2).post()`.
- `div` truncates toward 0 and `mod` takes the sign of the dividend, as in Java.
- `ift` exists only on relational expressions: write `b.eq(1).ift(x, y)`, not `b.ift(x, y)`.
- `globalCardinality(..., closed = true)` forces every variable into the listed values.
- `m.max(m, x)` takes the result first: `max(IntVar max, IntVar[] vars)`. `count` takes the value first:
  `count(v, x, n)`.
- Real variables (`realVar`) need Ibex, which the image does not have. Scale to integers.
- Do not name your own class `Model`: it hides `org.chocosolver.solver.Model`.

## DCP-Bench (`choco_java`)

**Contract.** One `.java` file declaring `public class Submission` with
`public static void build(Instance inst, Model m, Outputs out)`, with no `main` and nothing on stdout.
Anything printed goes to stderr. The image compiles it against Choco 6.0.1, Gson 2.11.0 and the
driver classes `dcp.Instance` and `dcp.Outputs`, then the driver calls `build` and solves.

```java
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Row seating: seat n guests in a row of n chairs so that no two enemies sit side
// by side, and minimise the total distance from each guest's preferred chair.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    int[] preferred = inst.getIntArray("preferred");
    int[][] enemies = inst.getIntMatrix("enemies");
    IntVar[] seat = m.intVarArray("seat", n, 0, n - 1);   // seat[g]: chair of guest g
    IntVar[] guest = m.intVarArray("guest", n, 0, n - 1);  // guest[c]: guest on chair c

    // every chair holds exactly one guest
    m.inverseChanneling(seat, guest).post();

    // enemies never sit side by side
    for (int[] pair : enemies) m.distance(seat[pair[0]], seat[pair[1]], ">", 1).post();

    // minimise the total distance from the preferred chairs
    IntVar[] away = new IntVar[n];
    for (int g = 0; g < n; g++) away[g] = seat[g].dist(preferred[g]).intVar();
    IntVar total = m.sum("total", away);
    m.setObjective(Model.MINIMIZE, total);

    out.put("seat", seat);
    out.put("total", total);
  }
}
```

- **Data.** `Instance` reads the request JSON and names the field in its error message:
  - Scalars: `getInt`, `getLong`, `getBool`, `getDouble`, `getString`.
  - Lists: `getIntArray`, `getLongArray`, `getBoolArray`, `getStringArray`.
  - Nested lists: `getIntMatrix` (rows may be ragged) and `getInt3`.
  - `has(key)`, and `raw(key)` for any other shape as a Gson `JsonElement`.
  - JSON Booleans read as 0/1 where an int is asked for.
  - The brief's shapes are those of the example instance. Take every size, output lengths included, from the instance itself.
- **Outputs.** Call `out.put("name", value)` once for each name the brief declares, and no others. An extra name,
  such as the objective when it is not declared, is `invalid_output`.
  - A value is an `IntVar`, a `BoolVar` (written as 0/1), an `int`/`long`/`boolean` constant, or any nesting of arrays and Lists of these: `IntVar[]`, `IntVar[][]`, `BoolVar[][]`, `List.of(row1, row2)`, `IntVar[][][]`.
  - A number beyond the IntVar range goes through `out.putDigits("name", IntVar[] digits, 10)`, most significant digit first.
  - A derived value (a sum, a count) is output through an IntVar: `m.sum("total", x)` or `e.intVar()`.
- **Objective.** Call `m.setObjective(Model.MINIMIZE or Model.MAXIMIZE, v)` once, on an IntVar. Do not bound it
  with a value known from elsewhere.
- **Settings.** Optionally declare `public static SettingsBuilder settings()`. The driver passes its result
  to `new Model(...)`. This is the only way to turn on LCG (see above).
- **Search.** Set it in `build` with `m.getSolver().setSearch(...)` and restarts with `setLubyRestart`. Do
  not call `solve()`, `limitTime()` or `reset()` yourself: the driver owns the search.
- **Readability.** Open with a `//` line stating the problem, and start each constraint
  block with a `//` comment taken from the description's words, not the Choco call.

**What the driver does.** It calls `build`, extends your search strategy over every variable
(`makeCompleteStrategy`), and solves on one thread within the time limit.

- **Satisfaction:** it collects solutions up to the solution limit, distinct on the outputs. After each one it
  resets and posts a no-good on the declared outputs, so the next must also come quickly.
- **Optimisation:** it runs branch and bound until the search ends without a stop, and emits nothing
  before that. A stop before the proof is `timeout`. Then it rebuilds the model, fixes the objective
  to the optimum, and enumerates further optimal outputs the same way.
- **LCG:** under LCG every enumeration step rebuilds the model instead of resetting it.

An exception in `build`, or an `OutOfMemoryError`, comes back as `execution_error` with the Java message
in `detail`.

**Check.**
1. Run `python -m generation.brief PROBLEM` for the description, output names and shapes,
   objective direction and instance fields.
2. Run `python -m evaluation.check MODEL.java --problem PROBLEM --solver choco_java
   --instance-count 2 --solution-limit 2`. Each run compiles the model first.
3. Act on the `reason`:
   - `compilation_error`: fix the first javac error in stderr.
   - `invalid_output`: a declared name is missing, or a shape is wrong.
   - `invalid_solution`: a constraint is missing, wrong, or not posted.
   - `suboptimal_solution`/`no_solution`: the direction is wrong, or the model is overconstrained.
   - `execution_timeout`: use a global instead of a decomposition, `"AC"` on allDifferent, implied constraints, a better search, or restarts.
   - `execution_error`: an exception; its message is in `detail`.
4. "Declared outputs cannot extend to a reference solution" means the outputs break a
   convention of the description (0- or 1-based, order, a fixed first element). Reread
   the output sentence.
5. A top-level `accepted` can hide skipped instances, so read the per-instance reasons.
