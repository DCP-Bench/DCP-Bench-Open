# Choco 6.0.1 constraint catalogue

The public factory methods of `org.chocosolver.solver.Model`, grouped by need. They come from the
interfaces it implements (`IIntConstraintFactory`, `ISchedulingFactory`, `IReificationFactory`,
`ISatFactory`, `IDecompositionFactory`, `IResultVariableFactory`, `IVariableFactory`,
`IViewFactory`, `ISetConstraintFactory`, `IGraphConstraintFactory`), extracted from
`choco-solver-6.0.1-sources.jar`. Real-valued constraints are left out.

- A method returning `Constraint` does nothing until `.post()` is called, or until it is reified.
- A method returning `void` (the reification factory, `addClauses*`, the `*Dec` decompositions and
  2D `element`) posts at once.
- `op` is one of `"="`, `"!="`, `"<"`, `">"`, `"<="`, `">="`. In `arithm`, `op1` is `"+"`, `"-"`, `"*"`
  or `"/"`.
- **Verified:** the semantics in square brackets are checked against brute force in `catalogue.java`.
- **LCG:** "not under LCG" means the constraint throws or counts wrong with
  `SettingsBuilder.init().setLCG(true)` in 6.0.1.

## Variables

- `intVar(String name, int lb, int ub)`, `intVar(lb, ub)`, `intVar(String name, int[] values)`, and
  `intVar(int value)` for a constant.
- `intVar(name, lb, ub, boolean boundedDomain)`. With `true`, only bounds are kept. Use it for large
  ranges such as objectives, sums and times.
- `intVarArray(String name, int size, int lb, int ub)`, `intVarArray(size, lb, ub)`,
  `intVarArray(name, size, int[] values)`.
- `intVarMatrix(String name, int dim1, int dim2, int lb, int ub)` returns `IntVar[dim1][dim2]`.
- `boolVar(String name)`, `boolVar()`, `boolVar(boolean value)`, `boolVarArray(name, size)`, `boolVarMatrix(name, d1, d2)`.
- `BoolVar` extends `IntVar`, so a BoolVar goes anywhere an IntVar does, and `BoolVar[]` is an `IntVar[]`.
- `toBoolVar(IntVar... ivars)` casts 0/1 IntVars to BoolVars.
- `setVar(String name, int[] lb, int[] ub)` gives a set between its kernel `lb` and envelope `ub`.
  `setVar(int... values)` is a constant set, and `setVarArray(name, size, lb, ub)` makes several.
- `taskVar(IntVar s, int d)`, `taskVar(IntVar s, IntVar d)`, `taskVar(IntVar s, IntVar d, IntVar e)`.
  Alternatively `new Task(IntVar s, int d)` [s + d = e]. Optional tasks:
  `taskVar(s, d, BoolVar performed)`.
- Every IntVar bound must lie within ±21474836. `checkIntDomainRange` rejects bigger ones; the
  driver's 64-bit outputs go through digit variables.

## Views (no new propagator: a variable defined from another)

- `offset(x, c)` [x + c], `mul(x, a)` [a·x], `neg(x)` [−x], `abs(x)`, and `intView(a, x, b)` [a·x + b].
- `isEq(x, v)`, `isNeq(x, v)`, `isLeq(x, v)`, `isGeq(x, v)` each give a BoolVar equal to that test.
- `boolNotView(b)` and `b.not()`.
- Set views: `setBoolView(s, v)` [v ∈ s], `setBoolsView(s, size, offset)`, `boolsSetView(bools, offset)`,
  `intsSetView(ints, v, offset)` [the set of i with ints[i] = v], `setUnionView`,
  `setIntersectionView`, `setDifferenceView`.

## Arithmetic over a few variables

- `arithm(x, op, c)`, `arithm(x, op, y)`, `arithm(x, op1, y, op, c)`, `arithm(x, op1, y, op, z)`
  [`arithm(x, "+", y, "=", z)` is x + y = z; `arithm(x, "-", y, "<=", 1)` is x − y ≤ 1].
- `times(x, y, z)` [x·y = z], also `times(x, int, z)` and `times(x, y, int)`.
- `div(x, y, z)` [z = x / y truncated toward 0, y ≠ 0].
- `mod(x, y, z)` [z = x % y with the sign of x, Java semantics; y ≠ 0], `mod(x, int, z)`,
  `mod(x, int m, int r)`.
- `absolute(y, x)` [y = |x|], `square(y, x)` [y = x²], `pow(base, int exp, result)`,
  `pow(base, IntVar exp, result)`.
- `distance(x, y, op, c)` [|x − y| op c].
  - With an int constant, op is only `"="`, `"!="`, `"<"` or `">"`.
  - `distance(x, y, op, IntVar z)` takes `=`, `<=`, `>=`, `<` or `>`.
  - Not under LCG.
- `max(m, x, y)` and `min(m, x, y)`.
- `member(x, int[] values)`, `member(x, lb, ub)`, `notMember(x, values)`, `notMember(x, lb, ub)`.

## Expressions (`x.add(y).mul(2).le(z).post()`)

Every IntVar is an arithmetic expression (`ArExpression`):

- Arithmetic: `add`, `sub`, `mul` (each taking an int, an expression, or several), `div` [truncated], `mod`, `neg`, `abs`, `sqr`, `pow`.
- Bounds and distance: `min`, `max` (an int, an expression, or several), `dist` [|a − b|].

Comparisons give a relational expression (`ReExpression`): `eq`, `ne`, `lt`, `le`, `gt`, `ge`, `in(int...)`, `notin(int...)`. Relational expressions combine with
`and`, `or`, `xor`, `imp`, `iff` and `not`. `ift(a, b)` on a relational expression is the
if-then-else value [`v0.eq(v1.eq(1).ift(v2, 3))` is v0 = (v1 = 1 ? v2 : 3)].

- `e.post()` posts a relational expression.
- `e.intVar()` gives an IntVar equal to an arithmetic expression, and `r.boolVar()` a BoolVar equal to a relational one.
- `e.decompose()` returns the decomposition as a `Constraint`, and `e.extension()` returns a table built from the expression.

## Linear sums

- `sum(IntVar[] x, op, int c)`, `sum(x, op, IntVar s)`, `sum(BoolVar[] b, op, c or s)`
  [Σ x_i op c].
- `sum(IntVar[] x, op, IntVar[] y)` [Σx op Σy].
- `scalar(IntVar[] x, int[] coeffs, op, int c or IntVar s)` [Σ coeffs_i·x_i op c].
- Result variables: `sum(String name, IntVar... x)` returns an IntVar equal to the sum.
- Use an `IntVar` target when the sum is reused, and give it tight bounds from the data.

## Counting

- `count(int v, IntVar[] x, IntVar n)` [n = #{i : x_i = v}]. `count(IntVar v, x, n)` takes the
  value as a variable. `count(String name, v, x...)` returns n.
- `among(IntVar n, IntVar[] x, int[] values)` [n = #{i : x_i ∈ values}].
- `globalCardinality(IntVar[] x, int[] values, IntVar[] occ, boolean closed)`
  [occ_j = #{i : x_i = values_j}; closed: every x_i takes a value in `values`].
- `nValues(x, IntVar n)` [n = number of distinct values], `atMostNValues(x, n, boolean strong)`,
  and `atLeastNValues(x, n, boolean ac)`.
- `allEqual(x...)`, `notAllEqual(x...)`.

## Distinctness

- `allDifferent(IntVar... x)` and `allDifferent(x, "AC")`. Consistency is one of `"DEFAULT"`, `"AC"`, `"BC"`, `"FC"`, `"NEQS"`.
  Use `"AC"` for permutations, Latin squares and puzzles.
- `allDifferentExcept0(x)` [x_i ≠ x_j when both are nonzero] and
  `allDifferentExceptValues(x, int... values)`.
- `allDifferentUnderCondition(x, Condition c, boolean singleCondition)`.
- `allDiffPrec(x, int[][] predecessors, int[][] successors)`.
- Shifted copies (queens diagonals): `allDifferent` over `offset(q[i], i)` views.

## Element (indexing with a variable)

- `element(IntVar value, int[] table, IntVar index)` [value = table[index], index ∈ 0..n−1].
- `element(value, int[] table, index, int offset)` [value = table[index − offset]].
- `element(IntVar value, IntVar[] table, IntVar index, int offset)` for variables.
- `element(String name, int[] table, IntVar index)` returns the value variable.
- 2D: `element(value, int[][] matrix, row, rowOffset, col, colOffset)`, also with `IntVar[][]`.
  It posts at once (void).
  [It indexes the row-major flattening and **does not bound the column**: (row 0, col 2) reads
  matrix[1][0]. Post `arithm(col, "<", ncols)` yourself, or use an IntVar of the right domain.]

## Channelling

- `inverseChanneling(x, y)` [x_i = j ⇔ y_j = i, 0-based].
- `inverseChanneling(x, y, offsetX, offsetY)` [x_i = j + offsetX ⇔ y_j = i + offsetY].
- `boolsIntChanneling(BoolVar[] b, IntVar v, int offset)` [b_i = 1 ⇔ v = i + offset. It also
  keeps v in offset..offset+n−1, so exactly one b_i is 1].
- `bitsIntChanneling(BoolVar[] bits, IntVar v)` [v = Σ 2^i·bits_i].
- `clausesIntChanneling(IntVar v, BoolVar[] eq, BoolVar[] le)` [eq_i ⇔ v = lb+i, le_i ⇔ v ≤ lb+i].
- `setBoolsChanneling(BoolVar[] b, SetVar s)` [b_i = 1 ⇔ i ∈ s], with an offset variant.
- `setsIntsChanneling(SetVar[] sets, IntVar[] x)` [x_j = i ⇔ j ∈ sets_i].

## Order, lexicographic, symmetry breaking

- `increasing(x, int delta)` [x_{i+1} ≥ x_i + delta; 0 is nondecreasing, 1 strictly] and
  `decreasing(x, delta)`.
- `sort(x, y)` [y is x sorted nondecreasing] (not under LCG).
- `keySort(IntVar[][] x, IntVar[] perm, IntVar[][] sorted, int k)` sorts tuples by their first k
  columns. `perm` may be null.
- `lexLess(x, y)`, `lexLessEq(x, y)`, `lexChainLess(rows...)`, `lexChainLessEq(rows...)`.
- `intValuePrecedeChain(x, int[] v)` [v_{k+1} occurs only after the first v_k] and
  `intValuePrecedeChain(x, s, t)`. Use them for interchangeable values (colours, groups).

## Minimum, maximum, position

- `max(IntVar m, IntVar[] x)`, `min(m, x)`, plus BoolVar versions. Result variables:
  `max(String name, IntVar[] x)` and `min(name, x...)`.
- `argmax(IntVar z, int offset, IntVar[] x)` [z = first index of the maximum + offset],
  and `argmin(z, offset, x)` in the same way.

## Logic and reification

- Reified constraints:
  - `c.reify()` returns a BoolVar equal to the truth of c, and `c.reifyWith(BoolVar b)` uses a given one [b ⇔ c].
  - `c.implies(b)` [c ⇒ b] and `c.impliedBy(b)` [b ⇒ c].
- If-then forms (these post at once):
  - `ifThen(Constraint if, Constraint then)`, `ifThen(BoolVar if, then)`.
  - `ifThenElse(if, then, else)`, with an if-condition as a Constraint or a BoolVar.
  - `ifOnlyIf(c1, c2)`.
- `and(BoolVar...)`, `and(Constraint...)`, `or(BoolVar...)` and `or(Constraint...)` return a Constraint to post.
- `not(Constraint c)` is generic and can be weak. Under LCG it is wrong on globals: `not(allDifferent)` counted 0 solutions instead of 21.
- Single reified relations post at once:
  - Over two variables: `reifyXeqY(x, y, b)` [b ⇔ x = y], `reifyXneY`, `reifyXltY`, `reifyXgtY`, `reifyXleY`, `reifyXgeY`.
  - With a constant: `reifyXeqC(x, c, b)`, `reifyXneC`, `reifyXltC`, `reifyXgtC`, `reifyXinS(x, set, b)`, `reifyXnotinS`.
  - With an offset: `reifyXeqYC(x, y, c, b)` [b ⇔ x = y + c], `reifyXneYC`, `reifyXltYC`, `reifyXgtYC`.
  - Generic: `reifXrelC(x, op, c, b)` and `reifXrelYC(x, op, y, c, b)`.
- Half-reified (b ⇒ relation): `impXrelC(x, op, c, b)` and `impXrelYC(x, op, y, c, b)`.
- Clauses through the SAT layer (not under LCG):
  - `addClauses(LogOp tree)` and `addClauses(BoolVar[] pos, BoolVar[] neg)`.
  - `addClausesBoolOrArrayEqualTrue(b)`, `addClausesAtMostOne(b)`, `addClausesBoolAndArrayEqVar(b, t)` and the other `addClausesBool*` forms.
  - `LogOp.and/or/implies/ifOnlyIf/xor/nand/nor(...)` build the tree.
- `addConstructiveDisjunction(Constraint...)` gives a stronger `or` for a few alternatives.

## Extensional (tables, automata)

- `Tuples t = new Tuples(true); t.add(0, 1); t.add(new int[][]{{1, 2}, {2, 0}});` lists allowed tuples. With `new Tuples(false)` the tuples are forbidden.
- Then `table(IntVar[] x, t)` or `table(x, t, String algo)`, where algo is one of `"CT+"`, `"CT"`, `"MDD+"`, `"STR2+"`, `"GACSTR+"`, `"GAC2001"`, `"GAC3rm"`, `"GAC2001+"`, `"GAC3rm+"` or `"FC"`.
  - An algorithm ending in `+` rejects forbidden tuples.
  - Universal values work only with `CT`/`CT+` and `STR2+`.
  - `table(x1, x2, t)` is the binary form.
- Universal value: `new Tuples(int[][] tuples, boolean feasible, OptionalInt.of(star))`. [Calling
  `setUniversalValue` after `new Tuples(true)` has no effect in 6.0.1: the star then counts as an ordinary
  value.]
- `table(IntVar[] x, HybridTuples h)` takes tuples with conditions, and `mddc(x, MultivaluedDecisionDiagram mdd)` takes a decision diagram.
- `regular(IntVar[] x, IAutomaton a)` with `new FiniteAutomaton("0*1+0*")` (not under LCG):
  - In the regexp, a symbol is one digit, and a symbol of several digits goes in angle brackets: `"<10>2*"`.
  - Operators: `*`, `+`, `?`, `|`, `( )`, `{n,m}`.
  - To build the automaton by hand: `new FiniteAutomaton()`, `addState()`, `setInitialState`, `setFinal`, then `addTransition(from, to, symbols...)`.
- `costRegular(x, IntVar cost, ICostAutomaton a)` and `multiCostRegular(x, IntVar[] costs, a)`. Build the automaton with `CostAutomaton.makeSingleResource(automaton, int[][][] costs, inf, sup)`.

## Graphs over successor variables

- `circuit(IntVar[] succ)` [succ_i = next node; one cycle through all nodes, domain 0..n−1].
  `circuit(succ, offset)` [succ_i = j + offset], and `circuit(succ, offset, CircuitConf conf)`.
- `subCircuit(succ, offset, IntVar length)` [nodes with succ_i ≠ i form one cycle of `length`
  nodes; the others loop on themselves].
- `path(succ, IntVar start, IntVar end)` [a Hamiltonian path from start to end; **succ[end] = n**,
  so domain 0..n], and `path(succ, start, end, offset)`.
- `subPath(succ, start, end, offset, IntVar size)`.
- `tree(succ, IntVar nbTrees)` [a forest; root i has succ_i = i; nbTrees roots], with an offset variant
  (not under LCG).
- Tour cost: `element(c_i, costRow_i, succ_i)` per node, then `sum(c, "=", total)`.

## Packing and scheduling

- `binPacking(IntVar[] bin, int[] size, IntVar[] load, int offset)`
  [load_j = Σ size_i over bin_i = j + offset]. Bound `load` by the capacity.
- `knapsack(IntVar[] occ, IntVar weightSum, IntVar energySum, int[] weight, int[] energy)`
  [weightSum = Σ weight_i·occ_i and energySum = Σ energy_i·occ_i].
- `cumulative(IntVar[] starts, int[] durations, int[] heights, int capacity)`
  [at every time t, the heights of the tasks with s_i ≤ t < s_i + d_i sum to at most capacity].
- `cumulative(Task[] tasks, IntVar[] heights, IntVar capacity)`, also with a `List`.
  - With capacity 1 it is a disjunctive (one machine) constraint.
  - Optional tasks use `taskVar(..., BoolVar performed)`.
  - There is no separate `disjunctive` constraint, only the decomposition `disjunctiveDec(Task[], boolean strict)`.
- `diffN(IntVar[] x, IntVar[] y, IntVar[] w, IntVar[] h, boolean addCumulativeReasoning)`
  [rectangles (x_i, y_i, w_i, h_i) do not overlap; constant sizes via `intVar(c)`]. The k-dimensional form is
  `diffN(IntVar[][] origins, int[][] lengths)`.
- `ISchedulingFactory.setTimes(Task[])` is a search strategy for scheduling. Pass it to `solver.setSearch`.

## Decompositions (`void`, posted at once)

- Alternatives to globals: `amongDec`, `allDifferentExceptDec`, `globalCardinalityDec` (values as IntVar), `regularDec`, `binPackingDec`, `circuitDec`, `argmaxDec`, `argminDec`, `intValuePrecedeChainDec`.
- Scheduling: `cumulativeDec(starts, IntVar[] durations, heights, capacity)` (variable durations), `cumulativeTimeDec`, `disjunctiveDec(Task[], strict)`.
- `ifThenElseDec(BoolVar[] c, int[] or IntVar[] x, IntVar y)` [y = x_i for the first true c_i].
- `product(IntVar[][] A, B, C)` [matrix product A·B = C].
- `costFlow(int[] starts, int[] ends, int[] supplies, int[] unitCosts, IntVar[] flows, IntVar cost, int offset)`.

## Sets

- Unions and intersections:
  - `union(SetVar[] sets, SetVar u)`, `union(IntVar[] ints, SetVar u)` [u = the set of values], `union(u, indices, sets)`.
  - `intersection(sets, SetVar i)`.
- Relations between sets: `subsetEq(sets...)` [chain], `disjoint(a, b)`, `allDisjoint(sets...)`, `allDifferent(sets...)`, `allEqual(sets...)`, `partition(sets, universe)`, `symmetric`, `inverseSet(sets, inv, o1, o2)`, `offSet(a, b, k)` [b = a + k], and `setLe`/`setLt` (lexicographic order).
- Cardinality and emptiness: `s.getCard()` is an IntVar to constrain [|s|], `notEmpty(s)`, `nbEmpty(sets, n)`.
- Membership: `member(IntVar x, SetVar s)`, `member(int c, s)`, `notMember`, `member(SetVar[] sets, s)`.
- Weights and extremes:
  - `sum(SetVar s, IntVar total)` [Σ of the elements].
  - `sumElements(SetVar indices, int[] weights, IntVar total)` [Σ weights_i over i ∈ s], with an offset form.
  - `max(s, m, notEmpty)`, `min(s, m, notEmpty)`, and the weighted forms.
- `element(IntVar index, SetVar[] sets, SetVar s)`.
- `sortedSetIntsChanneling(s, IntVar[] ints, nullValue, offset)`.
- Sets do not work with LCG in 6.0.1 (ClassCastException).
- Outputs go through Booleans (`setBoolsChanneling`) or ints.

## Graph variables (`graphVar`, `digraphVar`)

`IGraphConstraintFactory` covers these constraints:

- Counts and loops: `nbNodes`, `nbEdges`, `loopSet` and `nbLoops`.
- Degrees: `minDegree(s)`, `maxDegree(s)` and `degrees`; directed graphs use the `In` and `Out` variants.
- Shape: `connected`, `biconnected`, `stronglyConnected`, `cycle`, `noCycle`, `noCircuit`, `tree`, `forest`, `directedTree(g, root)`, `directedForest` and `reachability(g, root)`.
- Components: `nbConnectedComponents` and `sizeConnectedComponents`.
- Graph measures: `nbCliques`, `diameter`, `subgraph`, `symmetric`, `antisymmetric` and `transitivity`.
- Optimisation: `tsp(g, cost, int[][] edgeCosts, lagrMode)` and `dcmst`.
- Channelling to Booleans: `nodesChanneling`, `edgeChanneling(g, b, i, j)`, `neighborsChanneling(g, BoolVar[][])`, `successorsChanneling(g, BoolVar[][])` and `predecessorsChanneling`. Outputs go through these Booleans.

A graph variable needs `UndirectedGraph`/`DirectedGraph` bounds from `org.chocosolver.util.objects.graphs`.
For routing, successor variables with `circuit`/`path` are simpler and are covered above.

## Search (`Solver solver = model.getSolver()`)

- `solver.setSearch(AbstractStrategy... s)` runs the strategies in order.
  - `Search.inputOrderLBSearch(x)` and `inputOrderUBSearch(x)` take variables in order, smallest or largest value first.
  - `Search.minDomLBSearch(x)` and `minDomUBSearch(x)` are first-fail.
  - Learning heuristics: `domOverWDegSearch(x)`, `domOverWDegRefSearch(x)`, `activityBasedSearch(x)`, `conflictHistorySearch(x)`, `failureRateBasedSearch(x)` and `failureLengthBasedSearch(x)`.
  - Other strategies: `randomSearch(x, seed)`, `roundRobinSearch(x)` and `Search.intVarSearch(x)` (dom/wdeg, best value when optimising).
  - Custom: `Search.intVarSearch(VariableSelector, IntValueSelector, IntVar...)`.
    - Variable selectors: `new FirstFail(model)`, `new InputOrder<>(model)`, `new Smallest()`, `new Largest()`, `new MaxRegret()`, `new DomOverWDeg<>(x, seed)`.
    - Value selectors: `new IntDomainMin()`, `new IntDomainMax()`, `new IntDomainMiddle(true)`, `new IntDomainMedian()`, `new IntDomainRandom(seed)`, `new IntDomainBest()`.
  - Wrappers: `Search.lastConflict(s)`, `Search.conflictOrderingSearch(s)`, `Search.bestBound(s)` and `Search.sequencer(s1, s2)`.
  - `Search.setVarSearch(sets...)` searches set variables.
- `makeCompleteStrategy(true)` extends a strategy over some variables to all of them. The DCP driver
  sets it.
- Restarts:
  - `solver.setLubyRestart(scale, new FailCounter(model, 1), maxRestarts)`, `setGeometricalRestart(base, factor, counter, max)`, `setLinearRestart`, `setConstantRestart`.
  - `setNoGoodRecordingFromRestarts()` keeps no-goods across restarts.
- Without a strategy, Choco uses `Search.defaultSearch(model)`, a black-box configuration with restarts.
- Limits: `limitTime("10s")`, `limitNode`, `limitFail`, `limitSolution`. Check `solver.getSearchState()` afterwards: `TERMINATED`
  means the search was exhausted and `STOPPED` means a limit was hit.
- LCG: `new Model("m", SettingsBuilder.init().setLCG(true))`. Under LCG, optimisation restarts on each
  solution.
