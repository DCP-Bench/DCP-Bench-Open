# Search: branching, restarts, implied constraints, symmetry

Reference: [integer branching](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelIntBranch.html),
[search engines](https://www.gecode.org/doc/6.2.0/reference/group__TaskSearch.html),
[cutoffs](https://www.gecode.org/doc/6.2.0/reference/classGecode_1_1Search_1_1Cutoff.html).
These lessons come from building and tuning a few hundred Gecode models.

## Contents
- [Branching](#branching)
- [Restarts](#restarts)
- [When the search is slow](#when-the-search-is-slow)
- [Limits](#limits)
- [Symmetry](#symmetry)

## Branching

- `branch(*this, x, VAR, VAL)` on an array; one variable takes only a value choice:
  `branch(*this, v, INT_VAL_MIN())`. Variables: `INT_VAR_SIZE_MIN()` (first fail),
  `INT_VAR_DEGREE_MAX()`, `INT_VAR_AFC_SIZE_MAX(0.99)` and `INT_VAR_CHB_SIZE_MAX()`
  (learn from failures; best with restarts), `INT_VAR_NONE()` (in order),
  `INT_VAR_MIN_MIN()`, `INT_VAR_REGRET_MIN_MAX()`, `tiebreak(a, b)`. Values:
  `INT_VAL_MIN()`, `INT_VAL_MAX()`, `INT_VAL_SPLIT_MIN()` (halve the domain: good on
  large domains and objectives), `INT_VAL_RND(Rnd(1))`. Booleans: `BOOL_VAR_NONE()`,
  `BOOL_VAR_RND(r)`, `BOOL_VAR_DEGREE_MAX()`, `BOOL_VAR_AFC_MAX(0.99)`,
  `BOOL_VAR_ACTION_MAX()`, `BOOL_VAR_CHB_MAX()` (no `_SIZE_` forms), `BOOL_VAL_MIN()`,
  `BOOL_VAL_MAX()`.
- Branch on the decisions that determine everything else; several `branch` calls run
  in order. Branch first on the few variables that decide the structure (a pattern, an
  assignment), then the rest, then the remaining auxiliaries so no variable is left
  open. Gecode reports a solution as soon as every brancher is done: an auxiliary that
  no branching and no propagation fixes stays unassigned, and a weak propagator on it
  may never have checked it. A model of three 0/1 variables under `distinct` (default
  level) with no branching on them was reported "solved" four times, its auxiliaries
  unassigned and one propagator still alive.
- Scheduling: branch on start times with `INT_VAR_MIN_MIN()`, `INT_VAL_MIN()` (the
  [job-shop example](../assets/jobshop-ft06/README.md) does this).
  Sequencing/routing: on successors with `INT_VAR_SIZE_MIN()`.
- Line or slot assignment with fixed totals and window limits (`sequence`, `count`):
  branch on the slots in order (`INT_VAR_NONE()`) and try the hardest value first;
  renumber values so the most constrained is smallest, or branch on a rank variable
  linked by `element`.

## Restarts

`RBS<T, BAB>` (or `RBS<T, DFS>`) with `Search::Options::cutoff =
Search::Cutoff::luby(scale)`, e.g. `luby(100)`, restarts the search with a growing
cutoff; it stays complete (the cutoff grows without bound). Pair it with AFC or CHB
branching, which learn across restarts. It is not a default: it can slow the
optimality proof. Example: [scheduling-machines-crew](../assets/scheduling-machines-crew/README.md).

## When the search is slow

- **On a timeout, first switch the search style**: in-order branching without restarts
  (`INT_VAR_NONE()`/`BOOL_VAR_NONE()`) against AFC or CHB with Luby restarts (scale
  100). Each won where the other timed out (an optimisation grid needed in-order; a
  pair-cover design needed AFC with restarts).
- Optimisation that finds a poor first solution and stalls: a search that builds good
  solutions first, or branch on the objective with `INT_VAL_SPLIT_MIN()`. Choices with
  a cost from a table: `element(*this, IntArgs(cost_i), choice_i, c_i)`, then branch on
  the `c_i` first (`INT_VAR_REGRET_MIN_MAX()`, `INT_VAL_MIN()`): cheapest choice first.
- Add implied prefix bounds to window limits: a limit of u per window of q allows at
  most `u*(t/q) + min(u, t%q)` in any t consecutive slots, so with a known total N the
  first t slots hold at least `N - that bound for the other n - t`. Post them with
  `linear` over the prefix Booleans.
- Weighted objective over a Boolean grid: one sum over all cells propagates weakly. Add
  partial sums per row and per column, each bounded by its cheapest and dearest
  feasible choices, and link them to the objective.
- Products of decision variables (`p_t * k_tv`) propagate weakly. Add the identities
  and bounds the rules imply: Σ_v p_t·k_tv = p_t·Σ_v k_tv, a lower bound on the
  objective (total demand / capacity, rounded up), per-item upper bounds. Implied
  constraints usually beat a change of heuristic.
- Stronger propagation in general: `IPL_DOM` where it is cheap, a global instead of a
  decomposition, redundant globals (`count` cards that sum to n, a `cumulative` beside
  `nooverlap` on each axis), tighter domains from the data.
- Enumerating by re-solving with the earlier solutions forbidden (blocking constraints
  posted on a fresh root) starts every later solution from scratch, so each must also
  come quickly: the same branching advice applies to them. A plain `DFS` loop on
  `next()` avoids this.

## Limits

A time, node or fail limit (`Search::Stop::time`, `Search::Stop::node`, `Search::Stop::fail`)
that fires before the search ends is not an answer. `engine.stopped()` tells it apart:
BAB then keeps its last solution, feasible but not proven optimal, and DFS may hold none,
so a stopped search with no solution is "unknown", not "infeasible". An enumeration cut
short is incomplete. When a small problem hits a limit, first switch the search style
(above), then raise the limit.

## Symmetry

`Symmetries syms; syms << VariableSymmetry(x) << ValueSymmetry(IntArgs(..));
branch(*this, x, VAR, VAL, syms);` (LDSB; also `VariableSequenceSymmetry(x, len)` for
interchangeable rows). Or post `precede` / lexicographic `rel`. Never both on the same
symmetry. Breaking symmetry removes solutions: leave it out when every solution must be
listed.
