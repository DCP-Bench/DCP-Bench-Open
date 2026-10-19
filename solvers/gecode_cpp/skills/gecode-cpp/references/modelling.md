# Modelling details: variables, data, MiniModel, propagation levels

Guide: [MPG](https://www.gecode.org/doc-latest/MPG.pdf), parts M (modelling) and B
(branching). Reference: [integer variables and constraints](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelInt.html),
[MiniModel](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelMiniModel.html).

## Contents
- [Variables and arrays](#variables-and-arrays)
- [Reading data from a JSON file](#reading-data-from-a-json-file)
- [MiniModel expressions](#minimodel-expressions)
- [Propagation levels](#propagation-levels)
- [Recipes](#recipes)

## Variables and arrays

- `IntVarArray x(*this, n, lo, hi)` (member; always give bounds: `IntVarArray(*this, n)`
  and `BoolVarArray(*this, n)` leave the variables unset and crash at run time),
  `IntVar v(*this, lo, hi)`, domains from a set: `IntVar v(*this, IntSet({1, 3, 7}))`.
  `BoolVarArray`, `BoolVar` likewise (0/1).
- When sizes come from data, declare the member and create it in the constructor body:
  `x = IntVarArray(*this, n, lo, hi)`.
- A `BoolVar` is not an `IntVar`: it does not go into `IntVarArgs`, `mult`, or the
  count argument of `count`. In MiniModel it mixes freely (`expr(*this, x * b)`,
  `sum(bools)`). For a post function that needs an `IntVar`, link one with
  `channel(*this, b, x)` (x in 0..1), or declare the 0/1 variables as `IntVar`.
- `IntVarArgs` is a temporary list for posting (`IntVarArgs a; a << x[0] << y;`). It is
  not updated on copy: never keep one as a member to read later.
- `IntVarArgs` slices of an array share variables; that is how sub-arrays are passed.
- A variable may appear more than once in a `linear` list: each occurrence adds its
  coefficient (`linear(*this, IntArgs({1, 1, 1}), {x, x, y}, IRT_EQ, 4)` is 2x + y = 4).
- Variables that must be equal can be one variable: `x[j] = x[i]` in an
  `IntVarArgs`/`IntVarArray` makes both entries the same variable, which beats an
  equality constraint.
- `Matrix<IntVarArray> m(x, cols, rows)` ([Matrix](https://www.gecode.org/doc/6.2.0/reference/classGecode_1_1Matrix.html)):
  `m(c, r)` (column first), `m.row(r)`, `m.col(c)`, `m.slice(c0, c1, r0, r1)`.
  `x.slice(start, step, n)` for strides.
- Constants: `IntArgs({..})`, `IntArgs(std::vector<int>)`, `IntArgs(n)` then fill,
  `IntArgs::create(n, start, inc)` (n copies of v: `IntArgs::create(n, v, 0)`;
  `IntArgs(n, v)` does not compile); `IntSharedArray` for tables used by many
  `element`s.
- `IntSet` bounds are inclusive. From a `std::vector<int> v`: `IntSet(IntArgs(v))`;
  `IntSet(v)` on a non-const vector does not compile.
- `IntVar(*this, lo, hi)` throws `Int::OutOfLimits` beyond ±(2^31 − 2); products of
  large domains overflow: bound them. A number wider than that is modelled as digit
  variables (each `0..base−1`, most significant first) and assembled outside Gecode as
  a 64-bit integer.
- Tight domains from the data. An auxiliary defined by an expression: `IntVar t =
  expr(*this, sum(x))` takes its bounds from the expression.
- `TupleSet t(arity)`, then `finalize()` before posting; `TupleSet t;` throws on `add`.
  `DFA(reg)` compiles the regular expression once; reuse it for rows with the same clue.
- Sets: `SetVar`, `SetVarArray` (header `<gecode/set.hh>`, link `-lgecodeset`); read
  results through Booleans linked with `channel(*this, bools, s)`.
- Floats (`FloatVar`, `<gecode/float.hh>`) exist but are slow and inexact; scale to
  integers.
- Posting on a failed space is fine, but check `status()` before reading values.

## Reading data from a JSON file

C++ has no JSON library in its standard library; use header-only
[nlohmann/json](https://json.nlohmann.me/) (Debian/Ubuntu `nlohmann-json3-dev`, Homebrew
`nlohmann-json`; `#include <nlohmann/json.hpp>`, nothing to link). Complete program:
[json-roster](../assets/json-roster/README.md).

```cpp
std::ifstream in(argc > 1 ? argv[1] : "data.json");
nlohmann::json data = nlohmann::json::parse(in);           // throws json::parse_error
int n = data.at("n").get<int>();                           // at() throws if the key is missing
std::vector<int> w = data.at("w");                         // implicit conversion
int a = data.at("m")[i][j].get<int>();                     // nested
bool flag = data.at("optimize").get<bool>();
for (const auto& d : data.at("days_off")[w]) ... d.get<int>();   // ragged rows: each row has its own size()
```

Take every size from the data (`data.at("demand").size()`), never from the example
file. Keys the program does not read (`name`, `note`) are simply ignored. Pass the
`json` (by `const&`) to the space constructor and post everything there.

## MiniModel expressions

- `rel(*this, linear_or_bool_expr)` posts; `expr(*this, e)` returns a fresh `IntVar` or
  `BoolVar` equal to `e`. `sum(x)`, `sum(IntArgs(c), x)`, `element(IntArgs(t), i)`,
  `min`, `max`, `abs`, `*`, `/`, `%`, `ite`.
- Reification: `BoolVar b = expr(*this, x < y)`; `rel(*this, b == (x < y))`;
  half-reified with `rel(*this, x, IRT_EQ, y, imp(b))` (also `eqv`, `pmi`) on most
  post functions taking `Reify`.
- **Relations are not numbers**: `(x == 1) + (y == 1)` does not compile. Count with
  `count`, or sum `expr(*this, x == 1)` BoolVars.
- Combine relations with MiniModel: `rel(*this, b == ((x < y) && (u < v)))`,
  `expr(*this, a && b)`; `rel(home, b, BOT_AND, ...)` takes Booleans only.
- Pass a propagation level as the last argument: `expr(*this, sum(x), IPL_DOM)`.
- Do not name a member or local `count`, `sum`, `min`, `max`, `element`, `path`,
  `circuit`, `sequence` or `rel`: it hides the Gecode function of that name.

## Propagation levels

`IPL_DOM` makes a propagator remove every unsupported value; `IPL_BND` reasons on
bounds; `IPL_VAL` only on assigned values; `IPL_DEF` is the propagator's default.

- `distinct`: `IPL_DOM` for permutations, puzzles, Latin squares and anything with
  tight domains; the default (value) misses most pruning
  ([infeasible-pigeonhole](../assets/infeasible-pigeonhole/README.md): `IPL_DOM` fails
  4 pigeons in 3 holes at the root, the default needs a search).
- `linear`: the default is bounds; `IPL_DOM` only for few variables with small domains.
- Arithmetic (`*`, `sqr`, `abs`, `/`): keep the default. `IPL_DOM` on a product of two
  domains of 10^4 values exhausts memory.
- `element`, `extensional`, `channel` with Booleans, `count` with fixed values are
  already domain consistent.
- One-hot `channel(*this, bools, v, o)` makes exactly one Boolean true and keeps `v`
  in o..o+n−1. For "none" give it its own Boolean (index 0, offset 0).
- `count(x, cards, vals)` forces every `x_i` to take a value in `vals`; list every
  value `x` may take, with cardinality `IntSet(0, n)` for unconstrained ones.
- `path`: `succ[e] = n`, not a node. `circuit` over n nodes needs domain 0..n−1.
- `sequence` and a few other globals stay alive at solutions; that is harmless.

## Recipes

### Fewest colours (or groups used)

Minimise the number of distinct values in a list: `nvalues` takes an `IntVar` for the
count, `precede` removes the symmetry between interchangeable values, and BAB minimises
the count (`cost()` returns it). Shape of the constructor, with `n` nodes and `edges`:

```cpp
IntVarArray colour(*this, n, 0, n - 1);   // colour of each node
IntVar k(*this, 1, n);                    // number of distinct colours
for (auto [a, b] : edges) rel(*this, colour[a] != colour[b]);
nvalues(*this, colour, IRT_EQ, k, IPL_DOM);
IntArgs order(n);                         // colour j+1 may appear only after colour j
for (int j = 0; j < n; ++j) order[j] = j;
precede(*this, colour, order);
branch(*this, colour, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
branch(*this, k, INT_VAL_MIN());
```

The class derives from `IntMinimizeSpace` and returns `k` from `cost()`; the copy
constructor updates `colour` and `k`.
