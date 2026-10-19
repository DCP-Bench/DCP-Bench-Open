# Chuffed 0.14.0 C++ API cheat sheet

Signatures are copied from the 0.14.0 headers (tag `0.14.0`, commit
`f698d562`). **(header only)**: never compiled by us; **(tested)**: compiled and
run, most of them in the skill's runnable examples (`assets/`). Everything is in global
scope; include the headers listed in SKILL.md. Pitfalls are in SKILL.md's *Common
issues* and not repeated here.

Conventions: `x`, `y`, `z` are `IntVar*`; `b`, `r` are `BoolView`; `a`, `c`
are `int`; `vec<T>&` arguments are non-const lvalues (no temporaries, no
`std::vector`). Values are 32-bit `int`. Variables carry bounds within
+-500,000,000.

## Variables (`vars/modelling.h`, `vars/int-var.h`, `vars/bool-view.h`)

- `IntVar* newIntVar(int min, int max)` - one integer variable. It has no eager flag: `newIntVar(0, 8, true)` fails with "too many arguments". For one eager variable use `IntVar* v; createVar(v, lo, hi, true);` (tested).
- `void createVar(IntVar*& x, int min, int max, bool el = false)` - one variable into a pointer.
- `void createVars(vec<IntVar*>& x, int n, int min, int max, bool el = false)` - `n` variables appended to an empty vec.
- `void createVars(vec<vec<IntVar*>>& x, int n, int m, int min, int max, bool el = false)` - an `n` x `m` matrix.
- `void createVars(vec<BoolView>& x, int n)` and `void createVars(vec<vec<BoolView>>& x, int n, int m)` - Boolean variables.
- `BoolView newBoolVar(int min = 0, int max = 1)` - one Boolean.
- `IntVar* getConstant(int v)` - a fixed variable for `v`, cached per value.
- `bv_true`, `bv_false` - constant BoolViews; `~b` negates a named BoolView lvalue.
- `void bool2int(BoolView b, IntVar* y)` - `y = b` (0/1); `y` needs domain within 0..1. Use it to branch on, print or sum Booleans as integers.
- An `IntVar*` does not convert to `BoolView`: `BoolView r = x;` and `BoolView r(x);` fail
  with "conversion from 'IntVar*' to non-scalar type 'BoolView'". To get a Boolean tied to a
  0..1 IntVar, create the Boolean and link it (tested):
  `BoolView r = newBoolVar(); bool2int(r, x);`. Then reify onto `r`, e.g.
  `int_rel_reif(bins[i], IRT_EQ, b, r);`. (The header also defines `IntVar::operator BoolView()`
  on the dereferenced object, `BoolView r = *x;`, for a 0..1 variable; header only, untested.)
- `x->getLit(v, LR_EQ)` (also `LR_NE`, `LR_GE`, `LR_LE`) - literal "x rel v", usable as `BoolView(...)`. Needs an eager variable (`el = true`) for `LR_EQ`/`LR_NE`. Also `*x <= t`, `*x > t` produce literals.
- `void flatten(vec<vec<U>>& x, vec<U>& y)` and `void transpose(vec<vec<U>>& x, vec<vec<U>>& y)` - output must be empty.
- `vec<T>`: `push(e)`, `push()` (default element), `size()`, `operator[]`, `last()`, `pop()`, `growTo(n)`, `growTo(n, pad)`, `vec<vec<int>> t(k)` sized constructor. Build rows of a `vec<vec<int>>` (e.g. table tuples) with `t.push(); t.last().push(v);` (tested).
- Read values (`getVal()`) only inside `print` or the solution callback.

## Relation types

- `IntRelType`: `IRT_EQ`, `IRT_NE`, `IRT_LE`, `IRT_LT`, `IRT_GE`, `IRT_GT`. `!rel` negates a relation.
- `BoolRelType`: `BRT_AND`, `BRT_OR`, `BRT_XOR`, `BRT_EQ`, `BRT_EQ_REIF`, `BRT_NE`, `BRT_L_IMPL`, `BRT_R_IMPL`, and `_LE/_LT/_GE/_GT` with `_REIF` forms. Prefer the plain constants listed in the Boolean table below.

## Relations and linear constraints (`primitives/primitives.h`)

| Call | Meaning |
| --- | --- |
| `int_rel(x, rel, y, c = 0)` | `x rel y + c` |
| `int_rel(x, rel, c)` | `x rel c` (fix, bound or exclude a value) |
| `bin_linear(x, y, rel, c)` | `x + y rel c` |
| `int_linear(vec<int>& a, vec<IntVar*>& x, rel, int c, r = bv_true)` | `sum a[i]*x[i] rel c`, reified by `r` when given |
| `int_linear(vec<IntVar*>& x, rel, int c, r = bv_true)` | `sum x[i] rel c` |
| `int_linear(vec<int>& a, vec<IntVar*>& x, rel, IntVar* y, r = bv_true)` | `sum a[i]*x[i] rel y` |
| `int_linear(vec<IntVar*>& x, rel, IntVar* y, r = bv_true)` | `sum x[i] rel y` |
| `int_linear_imp(vec<int>& a, vec<IntVar*>& x, rel, int c, r = bv_true)` | `r -> sum a[i]*x[i] rel c` (header only) |
| `int_linear_dom(vec<int>& a, vec<IntVar*>& x, int c)` | `sum a[i]*x[i] = c`, domain consistent (header only) |
| `bool_linear(vec<BoolView>& x, rel, IntVar* y)` | `sum x[i] rel y`, count of true Booleans; for a constant bound pass `getConstant(k)` (tested) |
| `bool_linear_decomp(vec<BoolView>& x, rel, int k)` or `(..., IntVar* kv)` | same, decomposed (header only) |

Put constants of a linear sum into `c`. A weighted sum with a variable result
needs a result variable: `int_linear(coefs, vars, IRT_EQ, result)`.

## Arithmetic: every call writes into a result variable

| Call | Meaning |
| --- | --- |
| `int_plus(x, y, z)` | `z = x + y` |
| `int_minus(x, y, z)` | `z = x - y` |
| `int_times(x, y, z)` | `z = x * y` |
| `int_div(x, y, z)` | `z = x / y`, rounding is not stated in the header (header only; check on a negative case) |
| `int_mod(x, y, z)` | do not use: compiles but aborts at run time with "arithmetic.cpp:691: Not yet supported" (tested). Encode `x = q*y + r`, `0 <= r < y` with `int_linear` instead; for parity `x = 2*h + r`, `r` in 0..1 |
| `int_abs(x, y)` | `y = abs(x)` |
| `int_pow(x, y, z)` | `z = x^y` (header only) |
| `int_min(x, y, z)` / `int_max(x, y, z)` | `z = min/max(x, y)` |
| `int_negate(x, y)` | `y = -x` (header only) |
| `minimum(vec<IntVar*>& x, IntVar* y)` / `maximum(...)` | `y = min/max of x` |
| `bool_arg_max(vec<BoolView>& x, int offset, IntVar* y)` | `y` is the index of the first true Boolean plus `offset` (header only) |

## Reification and Boolean logic

| Call | Meaning |
| --- | --- |
| `int_rel_reif(x, rel, y, r, c = 0)` | `r <-> (x rel y + c)` |
| `int_rel_reif(x, rel, int c, r)` | `r <-> (x rel c)` |
| `int_rel_half_reif(...)` | same shapes, only `r -> constraint` |
| `bool_rel(b, BRT_..., b2, b3 = bv_true)` | `t(b, b2, b3)`, for example `bool_rel(x, BRT_AND, y, z)` is `z <-> x and y`, `BRT_OR`, `BRT_XOR`, `BRT_EQ_REIF` (header only for most types) |
| `bool_clause(vec<BoolView>& pos, vec<BoolView>& neg)` | at least one of `pos` true or one of `neg` false |
| `bool_clause(vec<BoolView>& x)` | at least one of `x` true |
| `array_bool_or(vec<BoolView>& x, BoolView z)` | `z <-> or of x` |
| `array_bool_and(vec<BoolView>& x, BoolView z)` | `z <-> and of x` |
| `array_bool_or/and(vec<BoolView>& x, vec<BoolView>& y, BoolView z)` | with the `y` literals negated |

`int_linear(...)` with an `r` argument reifies a whole linear constraint.
Other globals have no reified form; encode them manually.

## Element

Indexing is `y = a[x - offset]`.

- `array_int_element(IntVar* x, vec<int>& a, IntVar* y, int offset = 0)` - constant array **(tested)**.
- `array_bool_element(IntVar* x, vec<bool>& a, BoolView y, int offset = 0)` (header only).
- `array_var_int_element_bound(IntVar* x, vec<IntVar*>& a, IntVar* y, int offset = 0)` - array of variables, bounds consistent; `array_var_int_element_dom(...)` same, domain consistent (header only).
- `array_var_bool_element(IntVar* x, vec<BoolView>& a, BoolView y, int offset = 0)` (header only).
- `array_var_int_element_bound_imp(const BoolView& b, x, a, y, offset)` - half-reified (header only).

## Global constraints (`globals/globals.h`)

| Call | Meaning |
| --- | --- |
| `all_different(vec<IntVar*>& x, ConLevel cl = CL_DEF)` | pairwise different; `CL_VAL`, `CL_BND`, `CL_DOM` choose consistency |
| `all_different_offset(vec<int>& a, vec<IntVar*>& x, cl = CL_DEF)` | `x[i] + a[i]` all different (queens diagonals) **(tested)** |
| `all_different_imp(const BoolView& b, x, cl)` | `b -> all_different(x)` (header only) |
| `inverse(vec<IntVar*>& x, vec<IntVar*>& y, int o1 = 0, int o2 = 0, cl)` | `x[i] = j <-> y[j] = i` with offsets (tested: inverse(cell, pos, 1, 0) for 1-based values) |
| `table(vec<IntVar*>& x, vec<vec<int>>& t)` | tuple of `x` is one of the rows of `t` **(tested)** |
| `regular(vec<IntVar*>& x, int q, int s, vec<vec<int>>& d, int q0, vec<int>& f)` | DFA with states `1..q`, symbols `1..s`, `d[state-1][symbol-1]` is the next state (0 rejects), start `q0`, accepting list `f` **(tested)** |
| `circuit(vec<IntVar*>& x, int offset = 0)` | successor array forms one Hamiltonian circuit **(tested)** |
| `subcircuit(vec<IntVar*>& x, int offset = 0)` | circuit on a subset, others point to themselves (header only) |
| `lex(vec<IntVar*>& x, vec<IntVar*>& y, bool strict)` | `x <=lex y` (or `<lex` with `strict`). Tested on ordinary integer rows; it crashed (signal 11) on rows of eager 0/1 variables, so avoid it there, and add it only when the problem allows that ordering |
| `value_precede_int(int s, int t, vec<IntVar*>& x)` | `s` occurs before `t` in `x` (header only) |
| `disjunctive(vec<IntVar*>& s, vec<int>& d)` | tasks with starts `s` and constant durations `d` do not overlap **(tested)** |
| `cumulative(vec<IntVar*>& s, vec<int>& d, vec<int>& r, int limit)` | constant durations, demands and capacity **(tested)** |
| `cumulative2(vec<IntVar*>& s, vec<IntVar*>& d, vec<IntVar*>& r, IntVar* limit)` | variable durations, demands, capacity (header only) |

Other 0.14.0 globals (graph constraints on BoolViews: `tree`, `connected`,
`mst`, `steiner_tree`, `path`, `dag`, `bounded_path`; `edit_distance`,
`cumulative_cal`, `blackbox`, `var_sym_break`, `val_sym_break`) have no
examples here. Read `globals.h` before using one.

## Branching and objective (`branching/branching.h`, `core/engine.h`)

- `void branch(vec<Branching*> x, VarBranch var, ValBranch val)` - search these variables first. Pass a named, flat `vec<IntVar*>`; it converts element-wise. Flatten a `vec<vec<IntVar*>>` grid first with `flatten(grid, flat)`. A `vec<BoolView>` does not compile ("cannot convert 'BoolView' to 'Branching*'"): branch on the 0/1 IntVars linked with `bool2int` instead (tested).
- Leftover variables: whatever no `branch` reaches stays unfixed in the reported solution. To hand the remaining literals to the SAT solver's activity search, add after your `branch` calls `so.vsids = true; engine.branching->add(&sat);` (`#include <chuffed/core/sat.h>`; tested on unbranched BoolViews, which `so.vsids` alone leaves unfixed).
- `VarBranch`: `VAR_DEFAULT`, `VAR_INORDER`, `VAR_SIZE_MIN`, `VAR_SIZE_MAX`, `VAR_MIN_MIN`, `VAR_MIN_MAX`, `VAR_MAX_MIN`, `VAR_MAX_MAX`, `VAR_DEGREE_MIN`, `VAR_DEGREE_MAX`, `VAR_REGRET_MIN_MAX`, `VAR_REGRET_MAX_MIN`, `VAR_ACTIVITY`, `VAR_RANDOM`.
- `ValBranch`: `VAL_DEFAULT`, `VAL_MIN`, `VAL_MAX`, `VAL_MIDDLE`, `VAL_MEDIAN`, `VAL_SPLIT_MIN`, `VAL_SPLIT_MAX`. `VAL_RANDOM` aborts at run time ("value selection branching is not yet supported").
- `void optimize(IntVar* v, int t)` - `t` is `OPT_MIN` or `OPT_MAX`; call once.
- `void output_vars(vec<IntVar*>& v)` / `output_var(Branching*)`: variables that distinguish solutions when enumerating (without it, search stops after the first solution); also used to print.

## Search options (global `so`)

Set them before `engine.solve` ([core/options.h](https://github.com/chuffed/chuffed/blob/0.14.0/chuffed/core/options.h)).

- Solutions and output: `so.nof_solutions` (default 1, 0 = all; ignored by optimisation, which runs to the proven optimum), `so.print_sol` (call `print` per solution), `so.time_out = std::chrono::milliseconds(ms)`.
- Search: `so.vsids` (activity-based search on the SAT literals).
- Restarts: library defaults have no restarts (`restart_scale` is effectively infinite). For hard or heavy-tailed search: `so.restart_type = LUBY; so.restart_scale = 1000;`. Scales of 100 to 600 left single instances unsolved on one car-sequencing set; 1000 solved all.
- Phase and activity: `so.toggle_vsids = true; so.sat_polarity = 2;` (anti-polarity). `so.branch_random` exists for randomised restarts. More in [performance.md](performance.md).

## Recipes

Each recipe uses a named variable per intermediate. `n`, `x`, etc. are your own.

Sum of products with constant coefficients (`total = sum c[i]*x[i]`):

```cpp
vec<int> c; vec<IntVar*> terms;            // push c[i] and x[i] in step
IntVar* total = newIntVar(lo, hi);          // lo, hi from the coefficients and domains
int_linear(c, terms, IRT_EQ, total);
```

Product of two variables: `int_times(x, y, p)` with `p` bounded by the
extreme products. For three or more factors chain through an intermediate.

Reified count (`count = number of i with x[i] == k`):

```cpp
vec<IntVar*> hits;
for (int i = 0; i < n; ++i) {
  BoolView b = newBoolVar();
  int_rel_reif(x[i], IRT_EQ, k, b);        // b <-> x[i] == k
  IntVar* h = newIntVar(0, 1);
  bool2int(b, h);
  hits.push(h);
}
IntVar* count = newIntVar(0, n);
int_linear(hits, IRT_EQ, count);
```

For a count of true BoolViews use `bool_linear(bools, IRT_EQ, count)`.

Absolute difference: `int_minus(x, y, d); int_abs(d, ad);` with `d` in
`[-M, M]` and `ad` in `[0, M]`.

Minimum and maximum: `maximum(vars, m)` and `minimum(vars, m)` for arrays;
`int_max(x, y, m)` for two. Minimizing a maximum: `maximum(load, peak);
optimize(peak, OPT_MIN);`.

Element on a 2-D table `T[r][c]` with variables `r`, `c`:

```cpp
vec<int> flat;                              // row-major copy of T
for (int i = 0; i < rows; ++i) for (int j = 0; j < cols; ++j) flat.push(T[i][j]);
vec<int> w; w.push(cols); w.push(1);
vec<IntVar*> rc; rc.push(r); rc.push(c);
IntVar* idx = newIntVar(0, rows * cols - 1);
int_linear(w, rc, IRT_EQ, idx);             // idx = cols*r + c
array_int_element(idx, flat, value);        // value = T[r][c]
```

Element with a 1-based index: `array_int_element(i, table, v, 1)`.

Implication and half reification (`p -> x >= 3`): create `BoolView p`, then
`int_rel_half_reif(x, IRT_GE, 3, p)`. Full equivalence uses `int_rel_reif`.
`p -> q` for BoolViews: `bool_rel(p, BRT_L_IMPL, q)` or the clause
`bool_clause(pos = {q}, neg = {p})`. Verify direction with a tiny model
before relying on `BRT_L_IMPL` (header only).

Conditional constraint `p -> sum(a*x) <= c`: `int_linear_imp(a, x, IRT_LE, c, p)`
(header only), or use the reified `int_linear(a, x, IRT_LE, c, p)` when
equivalence is acceptable.

Channeling between `x[i] = j` and a Boolean matrix `b[i][j]` over a domain
`0..m-1`: for each cell `int_rel_reif(x[i], IRT_EQ, j, b[i][j]);` and
`bool_linear` of each row equal to 1 if needed. Between two arrays use
`inverse(x, y)`.

Logical and/or of Booleans: `array_bool_and(vec, z)` and `array_bool_or(vec, z)`
define `z`; `bool_clause(vec)` asserts a disjunction.

Lexicographic order: `lex(a, b, false)` for `a <= b`, `lex(a, b, true)` for `a < b`.

Fixed value and exclusion: `int_rel(x, IRT_EQ, 3)`, `int_rel(x, IRT_NE, 3)`.

Index arithmetic over 2-D variable grids: keep a `vec<vec<IntVar*>>` from
`createVars(grid, rows, cols, lo, hi)`; flatten with `flatten(grid, flat)` into
an empty `vec<IntVar*>`; take columns with `transpose(grid, cols)`.

Print only the optimum (`so.print_sol = false`; the callback runs for each improving
solution during `optimize`, so the last values copied are the optimum; tested on a copy of
[knapsack-maximise](../assets/knapsack-maximise/README.md) with this change; `model` is the
`Knapsack*` made with `new`):

```cpp
std::vector<int> best;                              // values at the last improving solution
engine.setSolutionCallback([&] (Problem*) {
  best.clear();
  for (int i = 0; i < model->n; ++i) best.push_back(model->take[i]->getVal());
});
so.print_sol = false;
engine.solve(model);                                // model: the Knapsack* built with new
std::cout << "profit " << engine.best_sol << " take";
for (int b : best) std::cout << ' ' << b;
std::cout << "\n";
```

## Tips

- Eager variables (`el = true`) cost memory for large domains; use them for 0/1 variables, small domains, and anything read with `getLit`.
- Prefer one `int_linear` with a result variable to chains of `int_plus`.
