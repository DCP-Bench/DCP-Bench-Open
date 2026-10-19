---
name: gecode-cpp
description: Gecode, a propagation-based constraint programming solver used from C++ through gecode/int.hh, minimodel.hh and search.hh, with Space subclasses, global constraints, propagation levels and DFS/BAB search. Use when writing, debugging or explaining Gecode models in C++, choosing a global constraint or branching for one, or enumerating all (optimal) solutions with it.
license: Apache-2.0
compatibility: Requires a C++17 compiler and Gecode 6.2 (Debian/Ubuntu libgecode-dev; tested with 6.2.0, g++ 12.2); nlohmann/json (nlohmann-json3-dev) to read JSON data. MIT-licensed, no key or size limits.
metadata:
  domain: constraint-programming
  solver: gecode
  paradigm: cp
---

# Gecode (C++)

Gecode is a propagation-based CP solver with a large library of global constraints.
A model is a `Space` subclass: variables are members, constraints are posted in the
constructor, and search **copies** the space, so every member is updated in the copy
constructor. **Model with the globals.** Gecode's strength is its propagators; a
decomposition into pairwise `rel` or reified sums throws that away.

Docs: [Modeling and Programming with Gecode (MPG)](https://www.gecode.org/doc-latest/MPG.pdf),
the guide; [reference for 6.2.0](https://www.gecode.org/doc/6.2.0/reference/).

## Contents
- [Install](#install) · [Quick start](#quick-start) · [Constraint map](#constraint-map-read-the-description-pick-the-global)
- [Solving and statuses](#solving-and-statuses) · [All solutions](#all-solutions) · [Common issues](#common-issues) · [Further reading](#further-reading)
- References: [modelling.md](references/modelling.md) (variables, arrays, data, MiniModel, propagation levels), [search.md](references/search.md) (branching, restarts, implied constraints, symmetry), [constraints.md](references/constraints.md) (every post function), [catalogue.cpp](references/catalogue.cpp) (51 globals checked against brute force)
- Examples: [satisfy](assets/satisfy-send-more-money/README.md), [all solutions](assets/all-solutions-queens/README.md), [all optimal](assets/all-optimal-committee/README.md), [maximise](assets/maximise-knapsack/README.md), [minimise](assets/minimise-seating/README.md), [infeasible](assets/infeasible-pigeonhole/README.md), [scheduling](assets/scheduling-machines-crew/README.md), [job shop](assets/jobshop-ft06/README.md), [JSON input](assets/json-roster/README.md)

## Install

Debian/Ubuntu ([package](https://packages.debian.org/bookworm/libgecode-dev); ask before `sudo`):

```bash
sudo apt install g++ libgecode-dev nlohmann-json3-dev   # nlohmann only for JSON input
g++ -std=c++17 -O2 model.cpp -o model -lgecodesearch -lgecodeminimodel -lgecodeset \
    -lgecodefloat -lgecodeint -lgecodekernel -lgecodesupport && ./model
```

Headers land in `/usr/include/gecode`, libraries on the system path: no `-I`, `-L` or
`LD_LIBRARY_PATH` needed. Keep the library order above (dependants before
dependencies). macOS: `brew install gecode` ([formula](https://formulae.brew.sh/formula/gecode),
not tested here; add `-I`/`-L` for the Homebrew prefix). Other systems: build from
[source](https://github.com/Gecode/gecode) ([download page](https://www.gecode.org/download.html)).
Verify with the Quick start: it prints `Profit: 12 at x = 4, y = 0`.

## Quick start

```cpp
// Maximise 3x + 2y for integers 0 <= x, y <= 4 with x + y <= 4 and x + 3y <= 6.
#include <gecode/int.hh>
#include <gecode/minimodel.hh>
#include <gecode/search.hh>
#include <iostream>
using namespace Gecode;

class Plan : public IntMaximizeSpace {     // IntMinimizeSpace to minimise; Space to satisfy
 protected:
  IntVar x, y, profit;                      // everything read later is a member
 public:
  Plan() : x(*this, 0, 4), y(*this, 0, 4) {
    rel(*this, x + y <= 4);
    rel(*this, x + 3 * y <= 6);
    profit = expr(*this, 3 * x + 2 * y);    // a fresh IntVar with bounds from the expression
    branch(*this, IntVarArgs({x, y}), INT_VAR_SIZE_MIN(), INT_VAL_MIN());
  }
  Plan(Plan& s) : IntMaximizeSpace(s) {     // update EVERY variable member
    x.update(*this, s.x); y.update(*this, s.y); profit.update(*this, s.profit);
  }
  Space* copy() override { return new Plan(*this); }
  IntVar cost() const override { return profit; }   // the objective BAB improves
  void print() const { std::cout << "Profit: " << profit.val() << " at x = " << x.val() << ", y = " << y.val() << "\n"; }
};

int main() {
  Plan* root = new Plan;
  BAB<Plan> engine(root);                   // the engine searches its own clone
  delete root;
  Plan* best = nullptr;
  while (Plan* s = engine.next()) { delete best; best = s; }  // each one strictly better
  if (!best) { std::cout << (engine.stopped() ? "Stopped before a solution\n" : "No solution\n"); return 0; }
  best->print();
  if (engine.stopped()) std::cout << "(not proven optimal)\n";
  delete best;
}
```

## Constraint map: read the description, pick the global

Write the model clause by clause: for each sentence of the description find its row,
and start each block with a `//` comment in the description's words. Every call takes
the space first (`*this` in the constructor). Arrays are `IntVarArgs`/`IntVarArray`,
constants `IntArgs({..})`. Bracketed semantics are verified in [catalogue.cpp](references/catalogue.cpp);
signatures in [constraints.md](references/constraints.md); reference: [integer constraints](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelInt.html).

| The description says | Post |
|---|---|
| all different | [`distinct(*this, x, IPL_DOM)`](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelIntDistinct.html) |
| all different after shifts (queens diagonals) | `distinct(*this, IntArgs(offsets), x)` [x_i + n_i distinct] |
| all different except value c (0 = empty) | `distinct(*this, x, c)` |
| different where selected | `distinct(*this, bools, x)` [only x_i with b_i = 1] |
| exactly / at least / at most k equal to v | [`count(*this, x, v, IRT_EQ / IRT_GQ / IRT_LQ, k)`](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelIntCount.html); v or k may be an `IntVar`; v may be an `IntSet` |
| value v_j occurs c_j times (gcc) | `count(*this, x, cards, IntArgs(vals))`, cards `IntVarArgs`; bounds instead: `IntSetArgs` |
| number of distinct values | [`nvalues(*this, x, IRT_EQ, k)`](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelIntNValues.html) |
| the number of distinct values is to be minimised (colours, groups used) | `IntVar k(*this, 1, n)`, `nvalues(*this, x, IRT_EQ, k, IPL_DOM)`, then BAB on `k` with `precede` on the values; [recipe](references/modelling.md#recipes) |
| every window of q has l..u items in S | [`sequence(*this, x, IntSet(S), q, l, u)`](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelIntSequence.html) |
| two of them share a group at most once (pairs meet) | per pair: `BoolVarArgs m; m << expr(*this, g[p][r] == g[q][r])` over rounds r, then `linear(*this, m, IRT_LQ, 1)` |
| how many are true / weighted count | [`linear(*this, bools, IRT_EQ, k)`](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelIntLI.html), `linear(*this, IntArgs(w), x, IRT_LQ, cap)` [Σ w_i·x_i ≤ cap; w = 5m is `IntArgs({1, -5})` over `{w, m}`] |
| the i-th value of a table / array | [`element(*this, IntArgs(table), i, y)`](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelIntElement.html) [table[i] = y], `element(*this, xs, i, y)` for variables |
| a cell of a matrix indexed by variables | `element(*this, IntArgs(a), col, w, row, h, z)` [a[col + w*row] = z] |
| allowed combinations / compatibility table | [`TupleSet t(arity); t.add(IntArgs(..))...; t.finalize(); extensional(*this, x, t)`](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelIntExt.html); forbidden: `extensional(*this, x, t, false)` |
| a pattern along a sequence (nonogram row, shift rules) | `extensional(*this, x, DFA(reg))`, [`REG`](https://www.gecode.org/doc/6.2.0/reference/classGecode_1_1REG.html) built from `*r` (0+), `+r` (1+), `r(n, m)` (n..m times), `a + b` (concat), `a \| b` |
| visit every node once and return (tour) | [`circuit(*this, succ)`](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelIntGraph.html) [succ[i] = next node], with offset `circuit(*this, 1, succ)` |
| tour cost | `circuit(*this, IntArgs(cost), succ, total)` [cost row-major n×n; total = Σ cost[i][succ_i]] |
| Hamiltonian path from s to e | `path(*this, succ, s, e)` [succ has n vars, domain 0..n; succ[e] = n] |
| one task at a time on a machine | [`unary(*this, start, IntArgs(dur))`](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelIntScheduling.html); optional tasks: add `bools` |
| tasks of a job run in order (job shop) | `rel(*this, s_a + d_a <= s_b)` for each consecutive pair, plus one `unary` per machine; [job shop](assets/jobshop-ft06/README.md) |
| resource capacity over time | `cumulative(*this, cap, start, IntArgs(dur), IntArgs(use))`; optional tasks: add `bools`; machine choice: `cumulatives` |
| items into bins with capacities | [`binpacking(*this, load, bin, IntArgs(size))`](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelIntBinPacking.html) [load_j = Σ size_i over bin_i = j]; bound `load` by the capacity |
| rectangles do not overlap | [`nooverlap(*this, x, IntArgs(w), y, IntArgs(h))`](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelIntGeoPacking.html) |
| a sorted copy / order statistics | [`sorted(*this, x, y)`](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelIntSorted.html) |
| a permutation and its inverse (position ↔ item) | [`channel(*this, x, y)`](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelIntChannel.html) [x_i = j ⇔ y_j = i, both 0-based]; 1-based: `channel(*this, x, 1, y, 1)`; one-hot: `channel(*this, bools, v, offset)` |
| interchangeable values (colours, groups, labels) | [`precede(*this, x, IntArgs({0,1,..,k}))`](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelIntPrecede.html) [value v+1 appears only after v]; LDSB: [search.md](references/search.md#symmetry) |
| interchangeable rows or columns | `rel(*this, rowA, IRT_LQ, rowB)` (lexicographic) |
| an unordered collection (faces of a die, a multiset, a group's members) | `rel(*this, block, IRT_LQ)` (sorted), when nothing fixes the order |
| increasing sequence | `rel(*this, x, IRT_LE)` |
| y is one of x | `member(*this, x, y)` |
| minimum / maximum / position of the maximum | [`min(*this, x, y)`, `max(*this, x, y)`, `argmax(*this, x, i)`](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelIntArith.html) [first index on ties] |
| a set (team, group, subset) | [`SetVar s(*this, IntSet::empty, lo, hi, cmin, cmax)`](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelSet.html), `cardinality`, `rel(*this, s1, SRT_DISJ, s2)`, `channel(*this, bools, s)`; read results through the bools |
| x differs from / equals y plus a constant | `rel(*this, x != y + c)`, `rel(*this, x == y + c)` (no `rel(x, IRT_NQ, y, c)` form) |
| arithmetic | [`rel(*this, x * y == z)`, `abs`, `/`, `%`, `sqr`, `pow(e, n)`](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelMiniModelArith.html), `divmod(*this, x, d, q, r)` |
| logic between conditions | [`rel(*this, (x == 1) >> (y != 1))`, `&&`, `\|\|`, `!`, `^`](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelMiniModelBool.html); `clause(*this, BOT_OR, pos, neg, 1)` |
| if-then-else value | `ite(*this, b, x, y, z)` or `rel(*this, z == ite(b_expr, x, y))` |

A decomposition is right only when no row fits. Two globals on the same variables are
fine (a `distinct` beside a `linear`); redundant globals often pay (`count` cards that
sum to n, a `cumulative` beside `nooverlap` on each axis). Pass `IPL_DOM` to `distinct`
on permutations and puzzles; keep the default on arithmetic ([propagation levels](references/modelling.md#propagation-levels)).
A variable may appear more than once in a `linear` list: each occurrence adds its coefficient.
`linear(*this, IntArgs({1, 1, 1}), xs, IRT_EQ, 4)` with `xs = {x, x, y}` posts 2x + y = 4
(checked with Gecode 6.2.0); sum the coefficients yourself when that reads better.

Branch on every decision variable ([search.md](references/search.md)).

## Solving and statuses

[Search engines](https://www.gecode.org/doc/6.2.0/reference/group__TaskSearch.html):
`DFS<T>` (satisfy, enumerate), `BAB<T>` (optimise; `T` derives from `IntMinimizeSpace`
/ `IntMaximizeSpace` and overrides `IntVar cost() const`), `RBS<T, DFS>` / `RBS<T, BAB>`
(restarts, `opts.cutoff = Search::Cutoff::luby(scale)`). The engine clones the root, so
`delete` it after constructing the engine. [Options](https://www.gecode.org/doc/6.2.0/reference/classGecode_1_1Search_1_1Options.html):
`opts.threads` (1 = deterministic), `opts.stop = Search::Stop::time(ms)` (also
`Search::Stop::node(n)`, `fail(n)`, [stop objects](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelSearchStop.html)).
Gecode has no status enum; read it from these:

| What you see | Meaning |
|---|---|
| `root->status() == SS_FAILED` before search | infeasible, proven by propagation alone |
| `next()` returns a space | a solution (BAB: strictly better than the previous one); read `x.val()` |
| `next()` returns `nullptr`, `engine.stopped()` false | search exhausted: no more solutions; for BAB the last solution is **optimal**, none at all means **infeasible** |
| `next()` returns `nullptr`, `engine.stopped()` true | a stop object fired: the last BAB solution is feasible, not proven; none means unknown |

`engine.statistics()` gives `node`, `fail`, `depth`. Errors: compile errors come from
g++ (long template messages; read the first `error:`); run-time errors are C++
exceptions derived from `Gecode::Exception`, uncaught they print
`terminate called after throwing an instance of 'Gecode::Int::OutOfLimits'` plus
`what()` on stderr and abort (exit 134). Buffered `std::cout` output is lost on abort.

## All solutions

`DFS` returns each solution once per assignment of the **branched** variables: loop on
`next()` until `nullptr` ([all-solutions-queens](assets/all-solutions-queens/README.md)).
Branch only on the variables whose values define a solution, and make every auxiliary
functionally determined by them (otherwise see [Common issues](#common-issues)). **All
optimal solutions**: prove the optimum with `BAB`, then build a fresh space with
`rel(*this, cost == optimum)` and enumerate it with `DFS`. `BAB` keeps requiring each
solution to beat the last, so it never yields a second solution of equal cost. The fresh
space can be the same class, given the optimum through its constructor (a default of -1
means optimise), as [all-optimal-committee](assets/all-optimal-committee/README.md) does.

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| Garbage values or a crash after search; constraints silently ignored | A member missing from the copy constructor | Update every `IntVarArray`, `IntVar`, `BoolVar*`, `SetVar*` member |
| A "solution" violates a constraint, or `val()` throws `Attempt to access value of unassigned variable` | A solution is reported once every brancher is done; an auxiliary no branching and no propagation fixes stays open (a weak propagator may still be alive: `PropagatorGroup::all.size(*s) > 0`) | Branch on every decision variable, auxiliaries last ([search.md](references/search.md)) |
| Crash at run time right after construction | `IntVarArray(*this, n)` / `BoolVarArray(*this, n)` leave variables unset | Always give bounds: `IntVarArray(*this, n, lo, hi)` |
| `Int::OutOfLimits` (`Number out of limits`) | Bounds beyond ±(2^31 − 2) (`Int::Limits::max` = 2147483646), or overflowing products of large domains | Bound intermediates; split wide numbers into digit variables |
| Values read after copy are stale | An `IntVarArgs` kept as a member is not updated on copy | Keep an `IntVarArray` member |
| `(x == 1) + (y == 1)` does not compile | Relations are not numbers | `count`, or sum `expr(*this, x == 1)` BoolVars |
| A `BoolVar` rejected by `IntVarArgs`, `mult`, `count`'s count argument | A `BoolVar` is not an `IntVar` | `channel(*this, b, x)` with x in 0..1, or declare 0/1 `IntVar`s; MiniModel mixes them freely |
| `IntSet(v)` on a vector, `IntArgs(n, v)` do not compile | No such overloads | `IntSet(IntArgs(v))`; `IntArgs::create(n, v, 0)` for n copies of v |
| `TupleSet t;` throws on `add`; table ignored | No arity, or not finalised | `TupleSet t(arity)`, then `t.finalize()` before posting |
| `path`/`circuit` fails at once | Wrong domain | `circuit` over n nodes: domain 0..n−1; `path`: `succ[e] = n` |
| One-hot `channel(bools, v, o)` gives no "none" choice | It makes exactly one Boolean true, `v` in o..o+n−1 | Give "none" its own Boolean (index 0, offset 0) |
| gcc `count(x, cards, vals)` removes values | It forces every `x_i` into `vals` | List every value x may take, cardinality `IntSet(0, n)` for free ones |
| `rel(home, b, BOT_AND, ...)` rejects a relation | Takes Booleans only | `rel(*this, b == ((x < y) && (u < v)))`, `expr(*this, a && b)` |
| Odd compile error at `count(...)`, `sum(...)`, `element(...)` | A member or local named `count`, `sum`, `min`, `max`, `element`, `path`, `circuit`, `sequence` or `rel` hides the Gecode function | Rename it |
| Memory exhausted at posting | `IPL_DOM` on a product of two large domains (10^4 values) | Default level on arithmetic |
| All-optimal run returns one solution, never a second one of equal cost | `BAB` only reports strictly better solutions | Enumerate with `DFS` on a space with `rel(*this, cost == optimum)` ([All solutions](#all-solutions)) |
| `engine.stopped()` is true on a small problem: the answer is unknown or the list incomplete | A time, node or fail limit fired before the search ended | [Limits](references/search.md#limits): change the search style or raise the limit |
| Slow, or no first solution / optimum not proven | Weak propagation or branching | [search.md](references/search.md): implied constraints, branching order, restarts |
| `FloatVar` model slow or inexact | Floats are slow and inexact | Scale to integers |
| Values read from a failed space | — | Check `status()` before reading |

`sequence` and a few other globals stay alive at solutions; that is harmless once all
branched variables are assigned.

## Further reading

- MPG (the guide, with Space, cloning, MiniModel, branching, search engines, LDSB): <https://www.gecode.org/doc-latest/MPG.pdf>
- API reference 6.2.0: <https://www.gecode.org/doc/6.2.0/reference/> ([Space](https://www.gecode.org/doc/6.2.0/reference/classGecode_1_1Space.html), [MiniModel](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelMiniModel.html), [branching](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelIntBranch.html))
- Examples shipped with Gecode: <https://github.com/Gecode/gecode/tree/release-6.2.0/examples> (`queens.cpp`, `money.cpp`, `golomb-ruler.cpp`, `job-shop.cpp`)
