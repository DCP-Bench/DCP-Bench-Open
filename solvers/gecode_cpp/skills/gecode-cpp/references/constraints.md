# Gecode 6.2.0 constraint catalogue

Every post function in the installed headers (libgecode-dev 6.2.0-5), grouped by need, floats left out. `home` is the space (`*this` in a constructor); `ipl` is an optional `IntPropLevel` (IPL_DEF, IPL_VAL, IPL_BND, IPL_DOM); `Reify r` is `eqv(b)`, `imp(b)` or `pmi(b)`; `irt` is IRT_EQ, IRT_NQ, IRT_LE, IRT_LQ, IRT_GR, IRT_GQ. The common globals are checked against brute force in `catalogue.cpp`.

## Domains

- `dom(home, IntVar x, int n, ipl)`
- `dom(home, const IntVarArgs&x, int n, ipl)`
- `dom(home, IntVar x, int l, int m, ipl)`
- `dom(home, const IntVarArgs&x, int l, int m, ipl)`
- `dom(home, IntVar x, const IntSet&s, ipl)`
- `dom(home, const IntVarArgs&x, const IntSet&s, ipl)`
- `dom(home, IntVar x, int n, Reify r, ipl)`
- `dom(home, IntVar x, int l, int m, Reify r, ipl)`
- `dom(home, IntVar x, const IntSet&s, Reify r, ipl)`
- `dom(home, IntVar x, IntVar d, ipl)`
- `dom(home, BoolVar x, BoolVar d, ipl)`
- `dom(home, const IntVarArgs&x, const IntVarArgs&d, ipl)`
- `dom(home, const BoolVarArgs&x, const BoolVarArgs&d, ipl)`

## Relations over integers (also lexicographic `rel(x, IRT_LQ, y)` and chains `rel(x, IRT_LE)` on arrays)

- `rel(home, IntVar x0, IntRelType irt, IntVar x1, ipl)`
- `rel(home, const IntVarArgs&x, IntRelType irt, IntVar y, ipl)`
- `rel(home, IntVar x, IntRelType irt, int c, ipl)`
- `rel(home, const IntVarArgs&x, IntRelType irt, int c, ipl)`
- `rel(home, IntVar x0, IntRelType irt, IntVar x1, Reify r, ipl)`
- `rel(home, IntVar x, IntRelType irt, int c, Reify r, ipl)`
- `rel(home, const IntVarArgs&x, IntRelType irt, ipl)`
- `rel(home, const IntVarArgs&x, IntRelType irt, const IntVarArgs&y, ipl)`
- `rel(home, const IntVarArgs&x, IntRelType irt, const IntArgs&y, ipl)`
- `rel(home, const IntArgs&x, IntRelType irt, const IntVarArgs&y, ipl)`

## Relations and logic over Booleans

- `rel(home, BoolVar x0, IntRelType irt, BoolVar x1, ipl)`
- `rel(home, BoolVar x0, IntRelType irt, BoolVar x1, Reify r, ipl)`
- `rel(home, const BoolVarArgs&x, IntRelType irt, BoolVar y, ipl)`
- `rel(home, BoolVar x, IntRelType irt, int n, ipl)`
- `rel(home, BoolVar x, IntRelType irt, int n, Reify r, ipl)`
- `rel(home, const BoolVarArgs&x, IntRelType irt, int n, ipl)`
- `rel(home, const BoolVarArgs&x, IntRelType irt, const BoolVarArgs&y, ipl)` — Post domain consistent propagator for relation between x and y.
- `rel(home, const BoolVarArgs&x, IntRelType irt, const IntArgs&y, ipl)` — Post domain consistent propagator for relation between x and y.
- `rel(home, const IntArgs&x, IntRelType irt, const BoolVarArgs&y, ipl)` — Post domain consistent propagator for relation between x and y.
- `rel(home, const BoolVarArgs&x, IntRelType irt, ipl)` — Post domain consistent propagator for relation between elements in x.
- `rel(home, BoolVar x0, BoolOpType o, BoolVar x1, BoolVar x2, ipl)` — Post domain consistent propagator for Boolean operation on x0 and x1
- `rel(home, BoolVar x0, BoolOpType o, BoolVar x1, int n, ipl)` — Post domain consistent propagator for Boolean operation on x0 and x1
- `rel(home, BoolOpType o, const BoolVarArgs&x, BoolVar y, ipl)` — Post domain consistent propagator for Boolean operation on x
- `rel(home, BoolOpType o, const BoolVarArgs&x, int n, ipl)` — Post domain consistent propagator for Boolean operation on x
- `clause(home, BoolOpType o, const BoolVarArgs&x, const BoolVarArgs&y, BoolVar z, ipl)` — Post domain consistent propagator for Boolean clause with positive variables x and negative variable
- `clause(home, BoolOpType o, const BoolVarArgs&x, const BoolVarArgs&y, int n, ipl)` — Post domain consistent propagator for Boolean clause with positive variables x and negative variable
- `ite(home, BoolVar b, IntVar x, IntVar y, IntVar z, ipl)`
- `ite(home, BoolVar b, BoolVar x, BoolVar y, BoolVar z, ipl)`

## Value precedence (symmetry breaking)

- `precede(home, const IntVarArgs&x, int s, int t, ipl)` — Post propagator that s precedes t in x
- `precede(home, const IntVarArgs&x, const IntArgs&c, ipl)` — Post propagator that successive values in c precede each other in x

## Membership

- `member(home, const IntVarArgs&x, IntVar y, ipl)`
- `member(home, const BoolVarArgs&x, BoolVar y, ipl)`
- `member(home, const IntVarArgs&x, IntVar y, Reify r, ipl)`
- `member(home, const BoolVarArgs&x, BoolVar y, Reify r, ipl)`

## Element: n[x0] = x1; matrix form a[x + w*y] = z

- `element(home, IntSharedArray n, IntVar x0, IntVar x1, ipl)`
- `element(home, IntSharedArray n, IntVar x0, BoolVar x1, ipl)`
- `element(home, IntSharedArray n, IntVar x0, int x1, ipl)`
- `element(home, const IntVarArgs&x, IntVar y0, IntVar y1, ipl)`
- `element(home, const IntVarArgs&x, IntVar y0, int y1, ipl)`
- `element(home, const BoolVarArgs&x, IntVar y0, BoolVar y1, ipl)`
- `element(home, const BoolVarArgs&x, IntVar y0, int y1, ipl)`
- `element(home, IntSharedArray a, IntVar x, int w, IntVar y, int h, IntVar z, ipl)`
- `element(home, IntSharedArray a, IntVar x, int w, IntVar y, int h, BoolVar z, ipl)`
- `element(home, const IntVarArgs&a, IntVar x, int w, IntVar y, int h, IntVar z, ipl)`
- `element(home, const BoolVarArgs&a, IntVar x, int w, IntVar y, int h, BoolVar z, ipl)`

## Distinct: plain; offsets (x_i + n_i distinct); optional (only b_i = 1); except value c

- `distinct(home, const IntVarArgs&x, ipl)`
- `distinct(home, const IntArgs&n, const IntVarArgs&x, ipl)`
- `distinct(home, const BoolVarArgs&b, const IntVarArgs&x, ipl)`
- `distinct(home, const IntVarArgs&x, int c, ipl)`

## Channelling: x_i = j iff y_j = i; Booleans x_i = 1 iff y = i + o

- `channel(home, const IntVarArgs&x, const IntVarArgs&y, ipl)`
- `channel(home, const IntVarArgs&x, int xoff, const IntVarArgs&y, int yoff, ipl)`
- `channel(home, BoolVar x0, IntVar x1, ipl)`
- `channel(home, const BoolVarArgs&x, IntVar y, int o=0, ipl)`

## Sorted: y is x sorted increasingly (z: the permutation)

- `sorted(home, const IntVarArgs&x, const IntVarArgs&y, ipl)` — Post propagator that y is x sorted in increasing order
- `sorted(home, const IntVarArgs&x, const IntVarArgs&y, const IntVarArgs&z, ipl)` — Post propagator that y is x sorted in increasing order

## Count: #{i : x_i = n (or in set, or = y_i)} irt m; gcc with cardinality vars or sets per value

- `count(home, const IntVarArgs&x, int n, IntRelType irt, int m, ipl)`
- `count(home, const IntVarArgs&x, const IntSet&y, IntRelType irt, int m, ipl)`
- `count(home, const IntVarArgs&x, IntVar y, IntRelType irt, int m, ipl)`
- `count(home, const IntVarArgs&x, const IntArgs&y, IntRelType irt, int m, ipl)`
- `count(home, const IntVarArgs&x, int n, IntRelType irt, IntVar z, ipl)`
- `count(home, const IntVarArgs&x, const IntSet&y, IntRelType irt, IntVar z, ipl)`
- `count(home, const IntVarArgs&x, IntVar y, IntRelType irt, IntVar z, ipl)`
- `count(home, const IntVarArgs&x, const IntArgs&y, IntRelType irt, IntVar z, ipl)`
- `count(home, const IntVarArgs&x, const IntVarArgs&c, ipl)` — Posts a global count (cardinality) constraint
- `count(home, const IntVarArgs&x, const IntSetArgs&c, ipl)` — Posts a global count (cardinality) constraint
- `count(home, const IntVarArgs&x, const IntVarArgs&c, const IntArgs&v, ipl)` — Posts a global count (cardinality) constraint
- `count(home, const IntVarArgs&x, const IntSetArgs&c, const IntArgs&v, ipl)` — Posts a global count (cardinality) constraint
- `count(home, const IntVarArgs&x, const IntSet&c, const IntArgs&v, ipl)` — Posts a global count (cardinality) constraint

## Number of distinct values: #{x_i} irt y

- `nvalues(home, const IntVarArgs&x, IntRelType irt, int y, ipl)`
- `nvalues(home, const IntVarArgs&x, IntRelType irt, IntVar y, ipl)`
- `nvalues(home, const BoolVarArgs&x, IntRelType irt, int y, ipl)`
- `nvalues(home, const BoolVarArgs&x, IntRelType irt, IntVar y, ipl)`

## Sequence: each window of q consecutive x has between l and u values in s

- `sequence(home, const IntVarArgs&x, const IntSet&s, int q, int l, int u, ipl)`
- `sequence(home, const BoolVarArgs&x, const IntSet&s, int q, int l, int u, ipl)`

## Extensional: x in TupleSet (pos = false: not in), or accepted by a DFA

- `extensional(home, const IntVarArgs&x, DFA d, ipl)` — Post domain consistent propagator for extensional constraint described by a DFA
- `extensional(home, const BoolVarArgs&x, DFA d, ipl)` — Post domain consistent propagator for extensional constraint described by a DFA
- `extensional(home, const IntVarArgs&x, const TupleSet&t, bool pos, ipl)`
- `extensional(home, const IntVarArgs&x, const TupleSet&t, bool pos, Reify r, ipl)`
- `extensional(home, const BoolVarArgs&x, const TupleSet&t, bool pos, ipl)`
- `extensional(home, const BoolVarArgs&x, const TupleSet&t, bool pos, Reify r, ipl)`

## Arithmetic: min, max, argmin/argmax (first index on ties), abs, mult, div, mod, sqr, sqrt, pow, nroot

- `min(home, IntVar x0, IntVar x1, IntVar x2, ipl)`
- `min(home, const IntVarArgs&x, IntVar y, ipl)`
- `max(home, IntVar x0, IntVar x1, IntVar x2, ipl)`
- `max(home, const IntVarArgs&x, IntVar y, ipl)`
- `argmin(home, const IntVarArgs&x, IntVar y, bool tiebreak=true, ipl)`
- `argmin(home, const IntVarArgs&x, int o, IntVar y, bool tiebreak=true, ipl)`
- `argmax(home, const IntVarArgs&x, IntVar y, bool tiebreak=true, ipl)`
- `argmax(home, const IntVarArgs&x, int o, IntVar y, bool tiebreak=true, ipl)`
- `argmin(home, const BoolVarArgs&x, IntVar y, bool tiebreak=true, ipl)`
- `argmin(home, const BoolVarArgs&x, int o, IntVar y, bool tiebreak=true, ipl)`
- `argmax(home, const BoolVarArgs&x, IntVar y, bool tiebreak=true, ipl)`
- `argmax(home, const BoolVarArgs&x, int o, IntVar y, bool tiebreak=true, ipl)`
- `abs(home, IntVar x0, IntVar x1, ipl)`
- `mult(home, IntVar x0, IntVar x1, IntVar x2, ipl)`
- `divmod(home, IntVar x0, IntVar x1, IntVar x2, IntVar x3, ipl)`
- `div(home, IntVar x0, IntVar x1, IntVar x2, ipl)`
- `mod(home, IntVar x0, IntVar x1, IntVar x2, ipl)`
- `sqr(home, IntVar x0, IntVar x1, ipl)`
- `sqrt(home, IntVar x0, IntVar x1, ipl)`
- `pow(home, IntVar x0, int n, IntVar x1, ipl)`
- `nroot(home, IntVar x0, int n, IntVar x1, ipl)`

## Linear over integers: sum a_i x_i irt c (or y)

- `linear(home, const IntVarArgs&x, IntRelType irt, int c, ipl)`
- `linear(home, const IntVarArgs&x, IntRelType irt, IntVar y, ipl)`
- `linear(home, const IntVarArgs&x, IntRelType irt, int c, Reify r, ipl)`
- `linear(home, const IntVarArgs&x, IntRelType irt, IntVar y, Reify r, ipl)`
- `linear(home, const IntArgs&a, const IntVarArgs&x, IntRelType irt, int c, ipl)`
- `linear(home, const IntArgs&a, const IntVarArgs&x, IntRelType irt, IntVar y, ipl)`
- `linear(home, const IntArgs&a, const IntVarArgs&x, IntRelType irt, int c, Reify r, ipl)`
- `linear(home, const IntArgs&a, const IntVarArgs&x, IntRelType irt, IntVar y, Reify r, ipl)`

## Linear over Booleans

- `linear(home, const BoolVarArgs&x, IntRelType irt, int c, ipl)`
- `linear(home, const BoolVarArgs&x, IntRelType irt, int c, Reify r, ipl)`
- `linear(home, const BoolVarArgs&x, IntRelType irt, IntVar y, ipl)`
- `linear(home, const BoolVarArgs&x, IntRelType irt, IntVar y, Reify r, ipl)`
- `linear(home, const IntArgs&a, const BoolVarArgs&x, IntRelType irt, int c, ipl)`
- `linear(home, const IntArgs&a, const BoolVarArgs&x, IntRelType irt, int c, Reify r, ipl)`
- `linear(home, const IntArgs&a, const BoolVarArgs&x, IntRelType irt, IntVar y, ipl)`
- `linear(home, const IntArgs&a, const BoolVarArgs&x, IntRelType irt, IntVar y, Reify r, ipl)`

## Bin packing: l_j = sum of s_i with b_i = j

- `binpacking(home, const IntVarArgs&l, const IntVarArgs&b, const IntArgs&s, ipl)`

## Rectangle packing (nooverlap): optional rectangles with o

- `nooverlap(home, const IntVarArgs&x, const IntArgs&w, const IntVarArgs&y, const IntArgs&h, ipl)`
- `nooverlap(home, const IntVarArgs&x, const IntArgs&w, const IntVarArgs&y, const IntArgs&h, const BoolVarArgs&o, ipl)`
- `nooverlap(home, const IntVarArgs&x0, const IntVarArgs&w, const IntVarArgs&x1, const IntVarArgs&y0, const IntVarArgs&h, const IntVarArgs&y1, ipl)`
- `nooverlap(home, const IntVarArgs&x0, const IntVarArgs&w, const IntVarArgs&x1, const IntVarArgs&y0, const IntVarArgs&h, const IntVarArgs&y1, const BoolVarArgs&o, ipl)`

## Scheduling: unary, cumulative, cumulatives (several machines); optional tasks with m

- `order(home, IntVar s0, int p0, IntVar s1, int p1, BoolVar b, ipl)` — Post propagators for ordering two tasks
- `cumulatives(home, const IntVarArgs&m, const IntVarArgs&s, const IntVarArgs&p, const IntVarArgs&e, const IntVarArgs&u, const IntArgs&c, bool at_most, ipl)` — Post propagators for the cumulatives constraint
- `cumulatives(home, const IntArgs&m, const IntVarArgs&s, const IntVarArgs&p, const IntVarArgs&e, const IntVarArgs&u, const IntArgs&c, bool at_most, ipl)` — Post propagators for the cumulatives constraint.
- `cumulatives(home, const IntVarArgs&m, const IntVarArgs&s, const IntArgs&p, const IntVarArgs&e, const IntVarArgs&u, const IntArgs&c, bool at_most, ipl)` — Post propagators for the cumulatives constraint.
- `cumulatives(home, const IntArgs&m, const IntVarArgs&s, const IntArgs&p, const IntVarArgs&e, const IntVarArgs&u, const IntArgs&c, bool at_most, ipl)` — Post propagators for the cumulatives constraint.
- `cumulatives(home, const IntVarArgs&m, const IntVarArgs&s, const IntVarArgs&p, const IntVarArgs&e, const IntArgs&u, const IntArgs&c, bool at_most, ipl)` — Post propagators for the cumulatives constraint.
- `cumulatives(home, const IntArgs&m, const IntVarArgs&s, const IntVarArgs&p, const IntVarArgs&e, const IntArgs&u, const IntArgs&c, bool at_most, ipl)` — Post propagators for the cumulatives constraint.
- `cumulatives(home, const IntVarArgs&m, const IntVarArgs&s, const IntArgs&p, const IntVarArgs&e, const IntArgs&u, const IntArgs&c, bool at_most, ipl)` — Post propagators for the cumulatives constraint.
- `cumulatives(home, const IntArgs&m, const IntVarArgs&s, const IntArgs&p, const IntVarArgs&e, const IntArgs&u, const IntArgs&c, bool at_most, ipl)` — Post propagators for the cumulatives constraint.
- `unary(home, const IntVarArgs&s, const IntArgs&p, ipl)` — Post propagators for scheduling tasks on unary resources
- `unary(home, const IntVarArgs&s, const IntArgs&p, const BoolVarArgs&m, ipl)` — Post propagators for scheduling optional tasks on unary resources
- `unary(home, const TaskTypeArgs&t, const IntVarArgs&flex, const IntArgs&fix, ipl)` — Post propagators for scheduling tasks on unary resources
- `unary(home, const TaskTypeArgs&t, const IntVarArgs&flex, const IntArgs&fix, const BoolVarArgs&m, ipl)` — Post propagators for scheduling optional tasks on unary resources
- `unary(home, const IntVarArgs&s, const IntVarArgs&p, const IntVarArgs&e, ipl)` — Post propagators for scheduling tasks on unary resources
- `unary(home, const IntVarArgs&s, const IntVarArgs&p, const IntVarArgs&e, const BoolVarArgs&m, ipl)` — Post propagators for scheduling optional tasks on unary resources
- `cumulative(home, int c, const TaskTypeArgs&t, const IntVarArgs&flex, const IntArgs&fix, const IntArgs&u, ipl)` — Post propagators for scheduling tasks on cumulative resources
- `cumulative(home, IntVar c, const TaskTypeArgs&t, const IntVarArgs&flex, const IntArgs&fix, const IntArgs&u, ipl)` — Post propagators for scheduling tasks on cumulative resources
- `cumulative(home, int c, const TaskTypeArgs&t, const IntVarArgs&flex, const IntArgs&fix, const IntArgs&u, const BoolVarArgs&m, ipl)` — Post propagators for scheduling optional tasks on cumulative resources
- `cumulative(home, IntVar c, const TaskTypeArgs&t, const IntVarArgs&flex, const IntArgs&fix, const IntArgs&u, const BoolVarArgs&m, ipl)` — Post propagators for scheduling optional tasks on cumulative resources
- `cumulative(home, int c, const IntVarArgs&s, const IntArgs&p, const IntArgs&u, ipl)` — Post propagators for scheduling tasks on cumulative resources
- `cumulative(home, IntVar c, const IntVarArgs&s, const IntArgs&p, const IntArgs&u, ipl)` — Post propagators for scheduling tasks on cumulative resources
- `cumulative(home, int c, const IntVarArgs&s, const IntArgs&p, const IntArgs&u, const BoolVarArgs&m, ipl)` — Post propagators for scheduling optional tasks on cumulative resources
- `cumulative(home, IntVar c, const IntVarArgs&s, const IntArgs&p, const IntArgs&u, const BoolVarArgs&m, ipl)` — Post propagators for scheduling optional tasks on cumulative resources
- `cumulative(home, int c, const IntVarArgs&s, const IntVarArgs&p, const IntVarArgs&e, const IntArgs&u, ipl)` — Post propagators for scheduling tasks on cumulative resources
- `cumulative(home, IntVar c, const IntVarArgs&s, const IntVarArgs&p, const IntVarArgs&e, const IntArgs&u, ipl)` — Post propagators for scheduling tasks on cumulative resources
- `cumulative(home, int c, const IntVarArgs&s, const IntVarArgs&p, const IntVarArgs&e, const IntArgs&u, const BoolVarArgs&m, ipl)` — Post propagators for scheduling optional tasks on cumulative resources
- `cumulative(home, IntVar c, const IntVarArgs&s, const IntVarArgs&p, const IntVarArgs&e, const IntArgs&u, const BoolVarArgs&m, ipl)` — Post propagators for scheduling optional tasks on cumulative resources

## Graphs: circuit over successors; cost matrix c row-major; path with x[e] = n

- `circuit(home, const IntVarArgs&x, ipl)` — Post propagator such that x forms a circuit
- `circuit(home, int offset, const IntVarArgs&x, ipl)` — Post propagator such that x forms a circuit
- `circuit(home, const IntArgs&c, const IntVarArgs&x, const IntVarArgs&y, IntVar z, ipl)` — Post propagator such that x forms a circuit with costs y and z
- `circuit(home, const IntArgs&c, int offset, const IntVarArgs&x, const IntVarArgs&y, IntVar z, ipl)` — Post propagator such that x forms a circuit with costs y and z
- `circuit(home, const IntArgs&c, const IntVarArgs&x, IntVar z, ipl)` — Post propagator such that x forms a circuit with cost z
- `circuit(home, const IntArgs&c, int offset, const IntVarArgs&x, IntVar z, ipl)` — Post propagator such that x forms a circuit with cost z
- `path(home, const IntVarArgs&x, IntVar s, IntVar e, ipl)` — Post propagator such that x forms a Hamiltonian path
- `path(home, int offset, const IntVarArgs&x, IntVar s, IntVar e, ipl)` — Post propagator such that x forms a Hamiltonian path
- `path(home, const IntArgs&c, const IntVarArgs&x, IntVar s, IntVar e, const IntVarArgs&y, IntVar z, ipl)` — Post propagator such that x forms a Hamiltonian path with costs y and z
- `path(home, const IntArgs&c, int offset, const IntVarArgs&x, IntVar s, IntVar e, const IntVarArgs&y, IntVar z, ipl)` — Post propagator such that x forms a Hamiltonian path with costs y and z
- `path(home, const IntArgs&c, const IntVarArgs&x, IntVar s, IntVar e, IntVar z, ipl)` — Post propagator such that x forms a Hamiltonian path with cost z
- `path(home, const IntArgs&c, int offset, const IntVarArgs&x, IntVar s, IntVar e, IntVar z, ipl)` — Post propagator such that x forms a Hamiltonian path with cost z

## Branching

- `branch(home, const IntVarArgs&x, IntVarBranch vars, IntValBranch vals, IntBranchFilter bf=nullptr, IntVarValPrint vvp=nullptr)` — Branch over x with variable selection vars and value selection vals
- `branch(home, const IntVarArgs&x, TieBreak<IntVarBranch> vars, IntValBranch vals, IntBranchFilter bf=nullptr, IntVarValPrint vvp=nullptr)` — Branch over x with tie-breaking variable selection vars and value selection vals
- `branch(home, IntVar x, IntValBranch vals, IntVarValPrint vvp=nullptr)` — Branch over x with value selection vals
- `branch(home, const BoolVarArgs&x, BoolVarBranch vars, BoolValBranch vals, BoolBranchFilter bf=nullptr, BoolVarValPrint vvp=nullptr)` — Branch over x with variable selection vars and value selection vals
- `branch(home, const BoolVarArgs&x, TieBreak<BoolVarBranch> vars, BoolValBranch vals, BoolBranchFilter bf=nullptr, BoolVarValPrint vvp=nullptr)` — Branch over x with tie-breaking variable selection vars and value selection vals
- `branch(home, BoolVar x, BoolValBranch vals, BoolVarValPrint vvp=nullptr)` — Branch over x with value selection vals
- `assign(home, const IntVarArgs&x, IntVarBranch vars, IntAssign vals, IntBranchFilter bf=nullptr, IntVarValPrint vvp=nullptr)` — Assign all x with variable selection vars with value selection vals
- `assign(home, const IntVarArgs&x, TieBreak<IntVarBranch> vars, IntAssign vals, IntBranchFilter bf=nullptr, IntVarValPrint vvp=nullptr)` — Assign all x with tie-breaking variable selection vars and value selection vals
- `assign(home, IntVar x, IntAssign vals, IntVarValPrint vvp=nullptr)` — Assign x with value selection vals
- `assign(home, const BoolVarArgs&x, BoolVarBranch vars, BoolAssign vals, BoolBranchFilter bf=nullptr, BoolVarValPrint vvp=nullptr)` — Assign all x with variable selection vars with value selection vals
- `assign(home, const BoolVarArgs&x, TieBreak<BoolVarBranch> vars, BoolAssign vals, IntBranchFilter bf=nullptr, IntVarValPrint vvp=nullptr)` — Assign all x with tie-breaking variable selection vars and value selection vals
- `assign(home, BoolVar x, BoolAssign vals, BoolVarValPrint vvp=nullptr)` — Assign x with value selection vals

## Branching with symmetry breaking (LDSB)

- `branch(home, const IntVarArgs&x, IntVarBranch vars, IntValBranch vals, const Symmetries&syms, IntBranchFilter bf=nullptr, IntVarValPrint vvp=nullptr)` — Branch over x with variable selection vars and value
- `branch(home, const IntVarArgs&x, TieBreak<IntVarBranch> vars, IntValBranch vals, const Symmetries&syms, IntBranchFilter bf=nullptr, IntVarValPrint vvp=nullptr)` — Branch over x with tie-breaking variable selection \a
- `branch(home, const BoolVarArgs&x, BoolVarBranch vars, BoolValBranch vals, const Symmetries&syms, BoolBranchFilter bf=nullptr, BoolVarValPrint vvp=nullptr)` — Branch over x with variable selection vars and value
- `branch(home, const BoolVarArgs&x, TieBreak<BoolVarBranch> vars, BoolValBranch vals, const Symmetries&syms, BoolBranchFilter bf=nullptr, BoolVarValPrint vvp=nullptr)` — Branch over x with tie-breaking variable selection \a
- `cbsbranch(home, const IntVarArgs&x)` — Branch over x using counting-based search
- `cbsbranch(home, const BoolVarArgs&x)` — Branch over x using counting-based search
- `relax(home, const IntVarArgs&x, const IntVarArgs&sx, Rnd r, double p)` — Branch over x using counting-based search
- `relax(home, const BoolVarArgs&x, const BoolVarArgs&sx, Rnd r, double p)` — Branch over x using counting-based search

## MiniModel linear expressions

- `LinIntExpr operator +(int, const IntVar&)`
- `LinIntExpr operator +(int, const BoolVar&)`
- `LinIntExpr operator +(int, const LinIntExpr&)`
- `LinIntExpr operator +(const IntVar&, int)`
- `LinIntExpr operator +(const BoolVar&, int)`
- `LinIntExpr operator +(const LinIntExpr&, int)`
- `LinIntExpr operator +(const IntVar&, const IntVar&)`
- `LinIntExpr operator +(const IntVar&, const BoolVar&)`
- `LinIntExpr operator +(const BoolVar&, const IntVar&)`
- `LinIntExpr operator +(const BoolVar&, const BoolVar&)`
- `LinIntExpr operator +(const IntVar&, const LinIntExpr&)`
- `LinIntExpr operator +(const BoolVar&, const LinIntExpr&)`
- `LinIntExpr operator +(const LinIntExpr&, const IntVar&)`
- `LinIntExpr operator +(const LinIntExpr&, const BoolVar&)`
- `LinIntExpr operator +(const LinIntExpr&, const LinIntExpr&)`
- `LinIntExpr operator -(int, const IntVar&)`
- `LinIntExpr operator -(int, const BoolVar&)`
- `LinIntExpr operator -(int, const LinIntExpr&)`
- `LinIntExpr operator -(const IntVar&, int)`
- `LinIntExpr operator -(const BoolVar&, int)`
- `LinIntExpr operator -(const LinIntExpr&, int)`
- `LinIntExpr operator -(const IntVar&, const IntVar&)`
- `LinIntExpr operator -(const IntVar&, const BoolVar&)`
- `LinIntExpr operator -(const BoolVar&, const IntVar&)`
- `LinIntExpr operator -(const BoolVar&, const BoolVar&)`
- `LinIntExpr operator -(const IntVar&, const LinIntExpr&)`
- `LinIntExpr operator -(const BoolVar&, const LinIntExpr&)`
- `LinIntExpr operator -(const LinIntExpr&, const IntVar&)`
- `LinIntExpr operator -(const LinIntExpr&, const BoolVar&)`
- `LinIntExpr operator -(const LinIntExpr&, const LinIntExpr&)`
- `LinIntExpr operator -(const IntVar&)`
- `LinIntExpr operator -(const BoolVar&)`
- `LinIntExpr operator -(const LinIntExpr&)`
- `LinIntExpr operator*(int, const IntVar&)`
- `LinIntExpr operator*(int, const BoolVar&)`
- `LinIntExpr operator*(const IntVar&, int)`
- `LinIntExpr operator*(const BoolVar&, int)`
- `LinIntExpr operator*(const LinIntExpr&, int)`
- `LinIntExpr operator*(int, const LinIntExpr&)`
- `LinIntExpr sum(const IntVarArgs&x)`
- `LinIntExpr sum(const IntArgs&a, const IntVarArgs&x)`
- `LinIntExpr sum(const BoolVarArgs&x)`
- `LinIntExpr sum(const IntArgs&a, const BoolVarArgs&x)`
- `LinIntExpr sum(const IntArgs&args)`

## MiniModel Boolean expressions

- `BoolExpr operator !(const BoolExpr&)`
- `BoolExpr operator&&(const BoolExpr&, const BoolExpr&)`
- `BoolExpr operator ||(const BoolExpr&, const BoolExpr&)`
- `BoolExpr operator ^(const BoolExpr&, const BoolExpr&)`
- `BoolExpr operator !=(const BoolExpr&, const BoolExpr&)`
- `BoolExpr operator==(const BoolExpr&, const BoolExpr&)`
- `BoolExpr operator >>(const BoolExpr&, const BoolExpr&)`
- `BoolExpr operator <<(const BoolExpr&, const BoolExpr&)`

## MiniModel reified domain tests

- `BoolExpr dom(const IntVar&x, int n)`
- `BoolExpr dom(const IntVar&x, int l, int m)`
- `BoolExpr dom(const IntVar&x, const IntSet&s)`
- `BoolExpr dom(const SetVar&x, SetRelType rt, int i)`
- `BoolExpr dom(const SetVar&x, SetRelType rt, int i, int j)`
- `BoolExpr dom(const SetVar&x, SetRelType rt, const IntSet&s)`

## MiniModel posting

- `IntVar expr(home, const LinIntExpr&e, const IntPropLevels&ipls=IntPropLevels::def)`
- `SetVar expr(home, const SetExpr&e)`
- `BoolVar expr(home, const BoolExpr&e, const IntPropLevels&ipls=IntPropLevels::def)`
- `rel(home, const BoolExpr&e, const IntPropLevels&ipls=IntPropLevels::def)`

## MiniModel arithmetic

- `LinIntExpr operator*(const LinIntExpr&x, const LinIntExpr&y)`
- `LinIntExpr operator /(const LinIntExpr&x, const LinIntExpr&y)`
- `LinIntExpr operator %(const LinIntExpr&x, const LinIntExpr&y)`
- `LinIntExpr abs(const LinIntExpr&e)`
- `LinIntExpr min(const LinIntExpr&x, const LinIntExpr&y)`
- `LinIntExpr min(const IntVarArgs&x)`
- `LinIntExpr max(const LinIntExpr&x, const LinIntExpr&y)`
- `LinIntExpr max(const IntVarArgs&x)`
- `LinIntExpr sqr(const LinIntExpr&x)`
- `LinIntExpr sqrt(const LinIntExpr&x)`
- `LinIntExpr pow(const LinIntExpr&x, int n)`
- `LinIntExpr nroot(const LinIntExpr&x, int n)`
- `LinIntExpr element(const IntVarArgs&x, const LinIntExpr&y)`
- `BoolExpr element(const BoolVarArgs&x, const LinIntExpr&y)`
- `LinIntExpr element(const IntArgs&x, const LinIntExpr&y)`
- `LinIntExpr ite(const BoolExpr&b, const LinIntExpr&x, const LinIntExpr&y)`

## MiniModel matrix sums

- `LinIntExpr sum(const Slice<IntArgs>&slice)`
- `LinIntExpr sum(const Matrix<IntArgs>&matrix)`

## Set domains and cardinality

- `dom(home, SetVar x, SetRelType r, int i)`
- `dom(home, const SetVarArgs&x, SetRelType r, int i)`
- `dom(home, SetVar x, SetRelType r, int i, int j)`
- `dom(home, const SetVarArgs&x, SetRelType r, int i, int j)`
- `dom(home, SetVar x, SetRelType r, const IntSet&s)`
- `dom(home, const SetVarArgs&x, SetRelType r, const IntSet&s)`
- `cardinality(home, SetVar x, unsigned int i, unsigned int j)`
- `cardinality(home, const SetVarArgs&x, unsigned int i, unsigned int j)`
- `dom(home, SetVar x, SetRelType rt, int i, Reify r)`
- `dom(home, SetVar x, SetRelType rt, int i, int j, Reify r)`
- `dom(home, SetVar x, SetRelType rt, const IntSet&s, Reify r)`
- `dom(home, SetVar x, SetVar d)`
- `dom(home, const SetVarArgs&x, const SetVarArgs&d)`

## Set relations

- `rel(home, SetVar x, SetRelType r, SetVar y)`
- `rel(home, SetVar x, SetRelType rt, SetVar y, Reify r)`
- `rel(home, SetVar s, SetRelType r, IntVar x)`
- `rel(home, IntVar x, SetRelType r, SetVar s)`
- `rel(home, SetVar s, SetRelType rt, IntVar x, Reify r)`
- `rel(home, IntVar x, SetRelType rt, SetVar s, Reify r)`
- `rel(home, SetVar s, IntRelType rt, IntVar x)`
- `rel(home, SetVar s, IntRelType rt, IntVar x, Reify r)`

## Set operations

- `rel(home, SetVar x, SetOpType op, SetVar y, SetRelType r, SetVar z)`
- `rel(home, SetOpType op, const SetVarArgs&x, SetVar y)`
- `rel(home, SetOpType op, const SetVarArgs&x, const IntSet&z, SetVar y)`
- `rel(home, SetOpType op, const IntVarArgs&x, const IntSet&z, SetVar y)`
- `rel(home, SetOpType op, const IntVarArgs&x, SetVar y)`
- `rel(home, const IntSet&x, SetOpType op, SetVar y, SetRelType r, SetVar z)`
- `rel(home, SetVar x, SetOpType op, const IntSet&y, SetRelType r, SetVar z)`
- `rel(home, SetVar x, SetOpType op, SetVar y, SetRelType r, const IntSet&z)`
- `rel(home, const IntSet&x, SetOpType op, SetVar y, SetRelType r, const IntSet&z)`
- `rel(home, SetVar x, SetOpType op, const IntSet&y, SetRelType r, const IntSet&z)`
- `ite(home, BoolVar b, SetVar x, SetVar y, SetVar z)`

## Set min, max, cardinality, weights

- `min(home, SetVar s, IntVar x)` — Post propagator that x is the minimal element of s and that s is not empty
- `notMin(home, SetVar s, IntVar x)` — Post propagator that x is not the minimal element of s
- `min(home, SetVar s, IntVar x, Reify r)` — Post reified propagator for b iff x is the minimal element of s
- `max(home, SetVar s, IntVar x)` — Post propagator that x is the maximal element of s and that s is not empty
- `notMax(home, SetVar s, IntVar x)` — Post propagator that x is not the maximal element of s
- `max(home, SetVar s, IntVar x, Reify r)` — Post reified propagator for b iff x is the maximal element of s
- `cardinality(home, SetVar s, IntVar x)`
- `cardinality(home, SetVar s, IntVar x, Reify r)`
- `weights(home, IntSharedArray elements, IntSharedArray weights, SetVar x, IntVar y)`

## Set channelling

- `channel(home, const IntVarArgs&x, const SetVarArgs&y)`
- `channelSorted(home, const IntVarArgs&x, SetVar y)`
- `channel(home, const BoolVarArgs&x, SetVar y)`
- `channel(home, const SetVarArgs&x, const SetVarArgs&y)`

## Set value precedence

- `precede(home, const SetVarArgs&x, int s, int t)` — Post propagator that s precedes t in x
- `precede(home, const SetVarArgs&x, const IntArgs&c)` — Post propagator that successive values in c precede each other in x

## Set element

- `element(home, SetOpType op, const SetVarArgs&x, SetVar y, SetVar z, const IntSet&u=IntSet(Set::Limits::min, Set::Limits::max))`
- `element(home, SetOpType op, const IntVarArgs&x, SetVar y, SetVar z, const IntSet&u=IntSet(Set::Limits::min, Set::Limits::max))`
- `element(home, SetOpType op, const IntSetArgs&x, SetVar y, SetVar z, const IntSet&u=IntSet(Set::Limits::min, Set::Limits::max))`
- `element(home, SetOpType op, const IntArgs&x, SetVar y, SetVar z, const IntSet&u=IntSet(Set::Limits::min, Set::Limits::max))`
- `element(home, const SetVarArgs&x, IntVar y, SetVar z)`
- `element(home, const IntSetArgs&s, IntVar y, SetVar z)`
- `element(home, const IntSetArgs&a, IntVar x, int w, IntVar y, int h, SetVar z)`
- `element(home, const SetVarArgs&a, IntVar x, int w, IntVar y, int h, SetVar z)`

## Set distinctness

- `atmostOne(home, const SetVarArgs&x, unsigned int c)`

## Set convexity

- `convex(home, SetVar x)`
- `convex(home, SetVar x, SetVar y)`

## Set sequence

- `sequence(home, const SetVarArgs&x)`
- `sequence(home, const SetVarArgs&y, SetVar x)`

## Set branching

- `branch(home, const SetVarArgs&x, SetVarBranch vars, SetValBranch vals, SetBranchFilter bf=nullptr, SetVarValPrint vvp=nullptr)` — Branch over x with variable selection vars and value selection vals
- `branch(home, const SetVarArgs&x, TieBreak<SetVarBranch> vars, SetValBranch vals, SetBranchFilter bf=nullptr, SetVarValPrint vvp=nullptr)` — Branch over x with tie-breaking variable selection vars and value selection vals
- `branch(home, SetVar x, SetValBranch vals, SetVarValPrint vvp=nullptr)` — Branch over x with value selection vals
- `assign(home, const SetVarArgs&x, SetVarBranch vars, SetAssign vals, SetBranchFilter bf=nullptr, SetVarValPrint vvp=nullptr)` — Assign all x with variable selection vars and value selection vals
- `assign(home, const SetVarArgs&x, TieBreak<SetVarBranch> vars, SetAssign vals, SetBranchFilter bf=nullptr, SetVarValPrint vvp=nullptr)` — Assign all x with tie-breaking variable selection vars and value selection vals
- `assign(home, SetVar x, SetAssign vals, SetVarValPrint vvp=nullptr)` — Assign x with value selection vals
- `branch(home, const SetVarArgs&x, SetVarBranch vars, SetValBranch vals, const Symmetries&syms, SetBranchFilter bf=nullptr, SetVarValPrint vvp=nullptr)` — Branch over x with variable selection vars and value
- `branch(home, const SetVarArgs&x, TieBreak<SetVarBranch> vars, SetValBranch vals, const Symmetries&syms, SetBranchFilter bf=nullptr, SetVarValPrint vvp=nullptr)` — Branch over x with tie-breaking variable selection \a
- `relax(home, const SetVarArgs&x, const SetVarArgs&sx, Rnd r, double p)` — Branch over x with tie-breaking variable selection \a

## MiniModel set expressions

- `SetExpr singleton(const LinIntExpr&)`
- `SetExpr operator -(const SetExpr&)`
- `SetExpr operator&(const SetExpr&, const SetExpr&)`
- `SetExpr operator |(const SetExpr&, const SetExpr&)`
- `SetExpr operator +(const SetExpr&, const SetExpr&)`
- `SetExpr operator -(const SetExpr&, const SetExpr&)`
- `SetExpr inter(const SetVarArgs&)`
- `SetExpr setunion(const SetVarArgs&)`
- `SetExpr setdunion(const SetVarArgs&)`
- `LinIntExpr cardinality(const SetExpr&)`
- `LinIntExpr min(const SetExpr&)`
- `LinIntExpr max(const SetExpr&)`
- `BoolExpr operator <=(const SetCmpRel&, const SetExpr&)`
- `BoolExpr operator >=(const SetCmpRel&, const SetExpr&)`
- `explicit BoolExpr(Misc*m)`
- `BoolVar expr(home, const IntPropLevels&ipls) const`
- `rel(home, const IntPropLevels&ipls) const`

## MiniModel set and integer relations

- `BoolExpr operator==(const SetExpr&s, const LinIntExpr&x)`
- `BoolExpr operator==(const LinIntExpr&x, const SetExpr&s)`
- `BoolExpr operator !=(const SetExpr&s, const LinIntExpr&x)`
- `BoolExpr operator !=(const LinIntExpr&x, const SetExpr&s)`
- `BoolExpr operator <=(const SetExpr&s, const LinIntExpr&x)`
- `BoolExpr operator <=(const LinIntExpr&x, const SetExpr&s)`
- `BoolExpr operator <(const SetExpr&s, const LinIntExpr&x)`
- `BoolExpr operator <(const LinIntExpr&x, const SetExpr&s)`
- `BoolExpr operator >=(const SetExpr&s, const LinIntExpr&x)`
- `BoolExpr operator >=(const LinIntExpr&x, const SetExpr&s)`
- `BoolExpr operator >(const SetExpr&s, const LinIntExpr&x)`
- `BoolExpr operator >(const LinIntExpr&x, const SetExpr&s)`
## Building tables and automata

- `TupleSet t(arity); t.add(IntArgs({..})); ...; t.finalize();` — `add` returns the set, so calls chain. `TupleSet(arity, dfa)` builds one from a DFA.
- `REG(v)` one symbol, `REG(IntArgs({..}))` any of the symbols, `a + b` concatenation, `a | b` choice, `*a` zero or more, `+a` one or more, `a(n, m)` n to m times, `a(n)` n or more. `DFA d(reg)`.
- `DFA(start, Transition[]{ {from, symbol, to}, ..., {-1, 0, 0} }, int final[]{ .., -1 })` for a hand-built automaton.

## Symmetries for LDSB

- `VariableSymmetry(x)`, `VariableSymmetry(x, IntArgs(indices))` — interchangeable variables.
- `VariableSequenceSymmetry(x, len)` — interchangeable consecutive blocks of `len` (rows of a matrix).
- `ValueSymmetry(IntArgs(values))`, `ValueSymmetry(IntSet)`, `ValueSymmetry(IntVar)` — interchangeable values.
- `ValueSequenceSymmetry(IntArgs(values), len)`.
- Combine with `Symmetries syms; syms << ... ;` and pass `syms` to `branch`.

## Branching heuristics

- Integer variable choice: `INT_VAR_NONE`, `INT_VAR_RND(r)`, `INT_VAR_SIZE_MIN/MAX`, `INT_VAR_DEGREE_MIN/MAX`, `INT_VAR_DEGREE_SIZE_MIN/MAX`, `INT_VAR_AFC_MIN/MAX(decay)`, `INT_VAR_AFC_SIZE_MIN/MAX(decay)`, `INT_VAR_ACTION_MIN/MAX`, `INT_VAR_ACTION_SIZE_MIN/MAX`, `INT_VAR_CHB_MIN/MAX`, `INT_VAR_CHB_SIZE_MIN/MAX`, `INT_VAR_MIN_MIN/MAX` (smallest/largest lower bound), `INT_VAR_MAX_MIN/MAX`, `INT_VAR_REGRET_MIN_MIN/MAX`, `INT_VAR_REGRET_MAX_MIN/MAX`, `INT_VAR_MERIT_MIN/MAX(f)`. Combine with `tiebreak(a, b, ...)`.
- Integer value choice: `INT_VAL_MIN`, `INT_VAL_MED`, `INT_VAL_MAX`, `INT_VAL_RND(r)`, `INT_VAL_SPLIT_MIN/MAX`, `INT_VAL_RANGE_MIN/MAX`, `INT_VALUES_MIN/MAX` (try all values in order).
- Booleans: `BOOL_VAR_NONE`, `BOOL_VAR_RND`, `BOOL_VAR_DEGREE_*`, `BOOL_VAR_AFC_*`, `BOOL_VAR_ACTION_*`, `BOOL_VAR_CHB_*`; values `BOOL_VAL_MIN/MAX/RND`.
- Sets: `SET_VAR_*` as for integers; values `SET_VAL_MIN_INC/EXC`, `SET_VAL_MAX_INC/EXC`, `SET_VAL_MED_INC/EXC`, `SET_VAL_RND_INC/EXC`.
