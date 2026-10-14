---
name: gecode-cpp
description: Write Gecode 6.2.0 constraint models in C++ that use its global constraints (distinct, count/gcc, element, extensional/regular, circuit/path, unary/cumulative, binpacking, nooverlap, sequence, channel, precede, sets) with the right propagation level and search. Also covers DCP-Bench Open submissions for the gecode_cpp integration (dcp::Space subclass, DCP_MODEL).
compatibility: Gecode 6.2.0 (Debian libgecode-dev 6.2.0-5), g++ 12, C++17. DCP-Bench use needs the repository and the image dcp-eval/gecode_cpp.
---

# Gecode 6.2.0 models in C++

Gecode is a propagation-based CP solver with a large library of global constraints.
A model is a `Space` subclass: variables are members, constraints are posted in the
constructor, search copies the space. **Model with the globals.** Gecode's strength is
its propagators; a decomposition into pairwise `rel` or reified sums throws that away.
Other files: [references/constraints.md](references/constraints.md) (every post
function, grouped), [references/catalogue.cpp](references/catalogue.cpp) (each global
checked against brute force), [references/examples.md](references/examples.md),
[sources.md](sources.md).

## Constraint map: read the description, pick the global

Write the model clause by clause: for each sentence of the description find its row
here. Every call takes the space first (`*this` in the constructor). Arrays are
`IntVarArgs`/`IntVarArray`, constants `IntArgs({..})`. Semantics in brackets are
verified in `catalogue.cpp`.

| The description says | Post |
|---|---|
| all different | `distinct(*this, x, IPL_DOM)` |
| all different after shifts (queens diagonals) | `distinct(*this, IntArgs(offsets), x)` [x_i + n_i distinct] |
| all different except value c (0 = empty) | `distinct(*this, x, c)` |
| different where selected | `distinct(*this, bools, x)` [only x_i with b_i = 1] |
| exactly / at least / at most k equal to v | `count(*this, x, v, IRT_EQ / IRT_GQ / IRT_LQ, k)`; v or k may be an `IntVar`; v may be an `IntSet` |
| value v_j occurs c_j times (gcc) | `count(*this, x, cards, IntArgs(vals))`, cards `IntVarArgs`; bounds instead: `IntSetArgs` |
| number of distinct values | `nvalues(*this, x, IRT_EQ, k)` |
| every window of q has l..u items in S | `sequence(*this, x, IntSet(S), q, l, u)` |
| two of them share a group at most once (pairs meet) | per pair: `BoolVarArgs m; m << expr(*this, g[p][r] == g[q][r])` over rounds r, then `linear(*this, m, IRT_LQ, 1)` |
| how many are true / weighted count | `linear(*this, bools, IRT_EQ, k)`, `linear(*this, IntArgs(w), x, IRT_LQ, cap)` [Σ w_i·x_i ≤ cap; w = 5m is `IntArgs({1, -5})` over `{w, m}`] |
| the i-th value of a table / array | `element(*this, IntArgs(table), i, y)` [table[i] = y], `element(*this, xs, i, y)` for variables |
| a cell of a matrix indexed by variables | `element(*this, IntArgs(a), col, w, row, h, z)` [a[col + w*row] = z] |
| allowed combinations / compatibility table | `TupleSet t(arity); t.add(IntArgs(..))...; t.finalize(); extensional(*this, x, t)`; forbidden: `extensional(*this, x, t, false)` |
| a pattern along a sequence (nonogram row, shift rules) | `extensional(*this, x, DFA(reg))`, `REG` built from `*r` (0+), `+r` (1+), `r(n, m)` (n..m times), `a + b` (concat), `a \| b` |
| visit every node once and return (tour) | `circuit(*this, succ)` [succ[i] = next node], with offset `circuit(*this, 1, succ)` |
| tour cost | `circuit(*this, IntArgs(cost), succ, total)` [cost row-major n×n; total = Σ cost[i][succ_i]] |
| Hamiltonian path from s to e | `path(*this, succ, s, e)` [succ has n vars, domain 0..n; succ[e] = n] |
| one task at a time on a machine | `unary(*this, start, IntArgs(dur))`; optional tasks: add `bools` |
| resource capacity over time | `cumulative(*this, cap, start, IntArgs(dur), IntArgs(use))`; optional tasks: add `bools`; machine choice: `cumulatives` |
| items into bins with capacities | `binpacking(*this, load, bin, IntArgs(size))` [load_j = Σ size_i over bin_i = j]; bound `load` by the capacity |
| rectangles do not overlap | `nooverlap(*this, x, IntArgs(w), y, IntArgs(h))` |
| a sorted copy / order statistics | `sorted(*this, x, y)` |
| a permutation and its inverse (position ↔ item) | `channel(*this, x, y)` [x_i = j ⇔ y_j = i, both 0-based]; 1-based: `channel(*this, x, 1, y, 1)`; one-hot: `channel(*this, bools, v, offset)` |
| interchangeable values (colours, groups, labels) | `precede(*this, x, IntArgs({0,1,..,k}))` [value v+1 appears only after v]; LDSB below |
| interchangeable rows or columns | `rel(*this, rowA, IRT_LQ, rowB)` (lexicographic) |
| an unordered collection (faces of a die, a multiset, a group's members) | `rel(*this, block, IRT_LQ)` (sorted), when the output does not fix the order |
| increasing sequence | `rel(*this, x, IRT_LE)` |
| y is one of x | `member(*this, x, y)` |
| minimum / maximum / position of the maximum | `min(*this, x, y)`, `max(*this, x, y)`, `argmax(*this, x, i)` [first index on ties] |
| a set (team, group, subset) | `SetVar s(*this, IntSet::empty, lo, hi, cmin, cmax)`, `cardinality`, `rel(*this, s1, SRT_DISJ, s2)`, `channel(*this, bools, s)`; outputs go through the bools |
| x differs from / equals y plus a constant | `rel(*this, x != y + c)`, `rel(*this, x == y + c)` (no `rel(x, IRT_NQ, y, c)` form) |
| arithmetic | `rel(*this, x * y == z)`, `abs`, `/`, `%`, `sqr`, `pow(e, n)`, `divmod(*this, x, d, q, r)` |
| logic between conditions | `rel(*this, (x == 1) >> (y != 1))`, `&&`, `\|\|`, `!`, `^`; `clause(*this, BOT_OR, pos, neg, 1)` |
| if-then-else value | `ite(*this, b, x, y, z)` or `rel(*this, z == ite(b_expr, x, y))` |

A decomposition is right only when no row fits. Two globals on the same variables are
fine (a `distinct` beside a `linear`); redundant globals often pay (`count` cards that
sum to n, a `cumulative` beside `nooverlap` on each axis).

## Program shape

```cpp
#include <gecode/int.hh>
#include <gecode/minimodel.hh>
#include <gecode/search.hh>
using namespace Gecode;

class Queens : public Space {
 protected:
  IntVarArray q;                                  // every variable you read later is a member
 public:
  Queens(int n) : q(*this, n, 0, n - 1) {
    // no two queens share a column or a diagonal
    distinct(*this, q, IPL_DOM);
    IntArgs up(n), down(n);
    for (int i = 0; i < n; ++i) { up[i] = i; down[i] = -i; }
    distinct(*this, up, q, IPL_DOM);
    distinct(*this, down, q, IPL_DOM);
    branch(*this, q, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
  }
  Queens(Queens& s) : Space(s) { q.update(*this, s.q); }   // update every member
  Space* copy() override { return new Queens(*this); }
};
// DFS<Queens> e(new Queens(8), opts); while (Queens* s = e.next()) { ...; delete s; }
```

- Optimisation: derive from `IntMinimizeSpace` / `IntMaximizeSpace`, implement
  `IntVar cost(void) const override`, search with `BAB<T>`. Restarts: `RBS<T, BAB>` with
  `Search::Options::cutoff = Search::Cutoff::luby(scale)`.
- Search options: `threads`, `stop = Search::Stop::time(ms)`; `engine.stopped()` tells a
  timeout from exhaustion.
- Link: `-lgecodesearch -lgecodeminimodel -lgecodeset -lgecodefloat -lgecodeint
  -lgecodekernel -lgecodesupport`.

## Variables, arrays, data

- `IntVarArray x(*this, n, lo, hi)` (member), `IntVar v(*this, lo, hi)`, domains from a
  set: `IntVar v(*this, IntSet({1, 3, 7}))`. `BoolVarArray`, `BoolVar` likewise (0/1).
- A `BoolVar` is not an `IntVar`: it does not go into `IntVarArgs`, `mult`, or the
  count argument of `count`. In MiniModel it mixes freely (`expr(*this, x * b)`,
  `sum(bools)`). For a post function that needs an `IntVar`, link one with
  `channel(*this, b, x)` (x in 0..1), or declare the 0/1 variables as `IntVar`.
- `IntVarArgs` is a temporary list for posting (`IntVarArgs a; a << x[0] << y;`). It is
  not updated on copy: never keep one as a member to read later.
- `Matrix<IntVarArray> m(x, cols, rows)`: `m(c, r)` (column first), `m.row(r)`,
  `m.col(c)`, `m.slice(c0, c1, r0, r1)`. `x.slice(start, step, n)` for strides.
- Constants: `IntArgs({..})`, `IntArgs(std::vector<int>)`, `IntArgs(n)` then fill,
  `IntArgs::create(n, start, inc)` (n copies of v: `IntArgs::create(n, v, 0)`; `IntArgs(n, v)`
  does not compile);
  `IntSharedArray` for tables used by many `element`s.
- Tight domains from the data. An auxiliary defined by an expression: `IntVar t =
  expr(*this, sum(x))` takes its bounds from the expression.

## MiniModel (expressions)

- `rel(*this, linear_or_bool_expr)` posts; `expr(*this, e)` returns a fresh `IntVar` or
  `BoolVar` equal to `e`. `sum(x)`, `sum(IntArgs(c), x)`, `element(IntArgs(t), i)`,
  `min`, `max`, `abs`, `*`, `/`, `%`, `ite`.
- Reification: `BoolVar b = expr(*this, x < y)`; `rel(*this, b == (x < y))`;
  half-reified with `rel(*this, x, IRT_EQ, y, imp(b))` (also `eqv`, `pmi`) on most
  post functions taking `Reify`.
- **Relations are not numbers**: `(x == 1) + (y == 1)` does not compile. Count with
  `count`, or sum `expr(*this, x == 1)` BoolVars.
- Pass a propagation level as the last argument: `expr(*this, sum(x), IPL_DOM)`.

## Propagation levels

`IPL_DOM` makes a propagator remove every unsupported value; `IPL_BND` reasons on
bounds; `IPL_VAL` only on assigned values; `IPL_DEF` is the propagator's default.
- `distinct`: `IPL_DOM` for permutations, puzzles, Latin squares and anything with
  tight domains; the default (value) misses most pruning.
- `linear`: the default is bounds; `IPL_DOM` only for few variables with small domains.
- Arithmetic (`*`, `sqr`, `abs`, `/`): keep the default. `IPL_DOM` on a product of two
  domains of 10^4 values exhausts memory.
- `element`, `extensional`, `channel` with Booleans, `count` with fixed values are
  already domain consistent.

## Search

- `branch(*this, x, VAR, VAL)`. Variables: `INT_VAR_SIZE_MIN()` (first fail),
  `INT_VAR_DEGREE_MAX()`, `INT_VAR_AFC_SIZE_MAX(0.99)` and `INT_VAR_CHB_SIZE_MAX()`
  (learn from failures; best with restarts), `INT_VAR_NONE()` (in order),
  `tiebreak(a, b)`. Values: `INT_VAL_MIN()`, `INT_VAL_MAX()`, `INT_VAL_SPLIT_MIN()`
  (halve the domain: good on large domains and objectives), `INT_VAL_RND(Rnd(1))`.
  Booleans: `BOOL_VAR_NONE()`, `BOOL_VAR_RND(r)`, `BOOL_VAR_DEGREE_MAX()`,
  `BOOL_VAR_AFC_MAX(0.99)`, `BOOL_VAR_ACTION_MAX()`, `BOOL_VAR_CHB_MAX()` (no `_SIZE_` forms),
  `BOOL_VAL_MIN()`, `BOOL_VAL_MAX()`.
- Branch on the decisions that determine everything else; several `branch` calls run
  in order. Then branch on the remaining auxiliaries so no variable is left open.
- Scheduling: branch on start times with `INT_VAR_MIN_MIN()`, `INT_VAL_MIN()`.
  Sequencing/routing: on successors with `INT_VAR_SIZE_MIN()`.
- Optimisation that finds a poor first solution and stalls: a search that builds good
  solutions first, or branch on the objective with `INT_VAL_SPLIT_MIN()`. Choices with
  a cost from a table: `element(*this, IntArgs(cost_i), choice_i, c_i)`, then branch on
  the `c_i` first (`INT_VAR_REGRET_MIN_MAX()`, `INT_VAL_MIN()`): cheapest choice first.
- Line or slot assignment with fixed totals and window limits (`sequence`, `count`):
  branch on the slots in order (`INT_VAR_NONE()`) and try the hardest value first;
  renumber values so the most constrained is smallest, or branch on a rank variable
  linked by `element`. Add implied prefix bounds: a limit of u per window of q allows at
  most `u*(t/q) + min(u, t%q)` in any t consecutive slots, so with a known total N the
  first t slots hold at least `N - that bound for the other n - t`. Post them with
  `linear` over the prefix Booleans.
- Symmetry: `Symmetries syms; syms << VariableSymmetry(x) << ValueSymmetry(IntArgs(..));
  branch(*this, x, VAR, VAL, syms);` (LDSB; also `VariableSequenceSymmetry(x, len)` for
  interchangeable rows). Or post `precede`/lex. Never both on the same symmetry.
- Weighted objective over a Boolean grid: one sum over all cells propagates weakly. Add
  partial sums per row and per column, each bounded by its cheapest and dearest
  feasible choices, and link them to the objective.
- Products of decision variables (`p_t * k_tv`) propagate weakly. Add the identities
  and bounds the rules imply: Σ_v p_t·k_tv = p_t·Σ_v k_tv, a lower bound on the objective
  (total demand / capacity, rounded up), per-item upper bounds. Implied constraints
  usually beat a change of heuristic.
- Heavy-tailed satisfaction search: AFC or CHB variable choice plus Luby restarts.

## Pitfalls

- Forgetting a member in the copy constructor compiles and then reads garbage or
  crashes. Update every `IntVarArray`, `IntVar`, `BoolVar*` and `SetVar*` member.
- Posting on a failed space is fine, but check `status()` before reading values.
- `IntVarArgs` slices of an array share variables; that is how sub-arrays are passed.
- `IntSet` bounds are inclusive. From a `std::vector<int> v`: `IntSet(IntArgs(v))`;
  `IntSet(v)` on a non-const vector does not compile. `IntVar(*this, lo, hi)` throws `Int::OutOfLimits`
  beyond ±(2^31 − 2); products of large domains overflow: bound them.
- `TupleSet` needs `finalize()` before posting. `DFA(reg)` compiles the regular
  expression once; reuse it for rows with the same clue.
- `path`: `succ[e] = n`, not a node. `circuit` over n nodes needs domain 0..n−1.
- One-hot `channel(*this, bools, v, o)` makes exactly one Boolean true and keeps `v`
  in o..o+n−1. For "none" give it its own Boolean (index 0, offset 0).
- Combine relations with MiniModel: `rel(*this, b == ((x < y) && (u < v)))`,
  `expr(*this, a && b)`; `rel(home, b, BOT_AND, ...)` takes Booleans only.
- `count(x, cards, vals)` forces every `x_i` to take a value in `vals`; list every value
  `x` may take, with cardinality `IntSet(0, n)` for unconstrained ones.
- `sequence` and a few other globals stay alive at solutions; that is harmless.
- Floats (`FloatVar`) exist but are slow and inexact; scale to integers.
- Do not name a member or local `count`, `sum`, `min`, `max`, `element`, `path`,
  `circuit`, `sequence` or `rel`: it hides the Gecode function of that name.

## DCP-Bench (`gecode_cpp`)

**Contract.** One `.cpp`, no `main`, nothing on stdout (log to `std::cerr`). It starts
with `#include "dcp.h"`, which includes the Gecode int, set, minimodel and search
headers and nlohmann JSON with `using namespace Gecode; using nlohmann::json;`. It
defines one class derived from `dcp::Space` and ends with `DCP_MODEL(ClassName)`.

```cpp
#include "dcp.h"

// Row seating: seat n guests in a row of n chairs so that no two enemies sit side
// by side, and minimise the total distance from each guest's preferred chair.
class Seating : public dcp::Space {
 protected:
  IntVarArray seat;   // seat[g]: chair of guest g
  IntVarArray guest;  // guest[c]: guest on chair c
  IntVar total;

 public:
  explicit Seating(const json& instance) {
    int n = instance.at("n");
    std::vector<int> preferred = instance.at("preferred");
    seat = IntVarArray(*this, n, 0, n - 1);
    guest = IntVarArray(*this, n, 0, n - 1);

    // every chair holds exactly one guest
    channel(*this, seat, guest, IPL_DOM);

    // enemies never sit side by side
    for (const auto& pair : instance.at("enemies"))
      rel(*this, abs(seat[pair[0].get<int>()] - seat[pair[1].get<int>()]) >= 2);

    // minimise the total distance from the preferred chairs
    IntVarArgs distance;
    for (int g = 0; g < n; ++g) distance << expr(*this, abs(seat[g] - preferred[g]));
    total = expr(*this, sum(distance));

    branch(*this, seat, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    minimize(total);
    output("seat", seat);
    output("total", total);
  }

  Seating(Seating& s) : dcp::Space(s) {
    seat.update(*this, s.seat);
    guest.update(*this, s.guest);
    total.update(*this, s.total);
  }
  Gecode::Space* copy() override { return new Seating(*this); }
};

DCP_MODEL(Seating)
```

- **Constructor** `explicit M(const json& instance)`, also when the instance has no
  fields (then `(void)instance;` and constants from the description, commented). Sizes
  come from the data, so create member arrays in the body: `x = IntVarArray(*this, n,
  lo, hi)`. Read data with `instance.at("n").get<int>()`, `std::vector<int> w =
  instance.at("w")`, `instance.at("m")[i][j].get<int>()`. The brief's shapes are those
  of the example instance; take every size from the instance itself.
- **Copy constructor** `M(M& s) : dcp::Space(s)` updates every member variable;
  `Gecode::Space* copy() override` returns `new M(*this)`. `dcp::Space` copies the
  outputs and the objective itself.
- **Outputs** (in the constructor, once per name the brief declares, no others: an
  extra name such as the objective is `invalid_output`): `output("name", v)` with
  an `IntVar`, `BoolVar`, `IntVarArray`/`IntVarArgs`, `BoolVarArray`/`BoolVarArgs`,
  `std::vector<IntVarArgs>` (one list per element), `Matrix<IntVarArray>` (one list per
  row: `m.row(r)` becomes the r-th inner list), an `int`, or a `std::vector<int>`. A
  derived value (a sum, a count) is an output through an `IntVar` made with `expr`.
- **Objective**: `minimize(v)` or `maximize(v)` once, on an `IntVar`
  (`total = expr(*this, sum(...))`). Do not bound it with a value known from elsewhere.
- **Restarts**: `restarts(100)` makes the driver use Luby restarts (still complete).
  Pair it with AFC or CHB branching.
- **Readability**: open with a `//` line stating the problem; start each constraint
  block with a `//` comment taken from the description's words, not the Gecode call.

**What the driver does.** It builds the model, posts a fallback branching over every
output and the objective after yours, and searches on one thread within the time limit.
Satisfaction: up to the solution limit, distinct on the outputs. Optimisation: branch
and bound (with restarts if requested) until the optimum is proven, emitting nothing
before; a stop before the proof is `timeout`. Then it fixes the objective and enumerates
further optimal outputs. The evaluator asks for two solutions: after the first, the
driver searches again from the root with that solution forbidden, so the second must
also come quickly. Branch first on the few variables that decide the structure (a
pattern, an assignment), then the rest. Variables that must be equal can be one
variable: `x[j] = x[i]` in an array shares it. Branch on all your decision variables
yourself: an auxiliary that no branching and no propagation fixes can give a wrong
solution, which the evaluator rejects.

**Check.**
1. `python -m generation.brief PROBLEM`: description, output names and shapes,
   objective direction, instance fields.
2. `python -m evaluation.check MODEL.cpp --problem PROBLEM --solver gecode_cpp
   --instance-count 2 --solution-limit 2` (each run compiles the model first).
3. By `reason`: `compilation_error`: fix the first error in the build log; `invalid_output`:
   a declared name is missing or a shape is wrong; `invalid_solution`: a constraint is
   missing or wrong; `suboptimal_solution`/`no_solution`: wrong direction or
   overconstrained; `execution_timeout`: stronger propagation (`IPL_DOM`, a global
   instead of a decomposition, redundant constraints), better branching, restarts;
   `execution_error`: an exception, its message is in `detail`.
4. "Declared outputs cannot extend to a reference solution": the outputs break a
   convention of the description (0- or 1-based, order, a fixed first element); reread
   the output sentence.
5. A top-level `accepted` can hide skipped instances: read the per-instance reasons.
