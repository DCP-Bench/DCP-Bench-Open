# FO(.) gotchas and modelling lessons

All verified against idp-engine 0.12.1 (z3-solver 4.11.2.0). Most were found while
writing several hundred FO(.) models for constraint and optimisation problems.

## Contents
- [Parsing and declarations](#parsing-and-declarations)
- [Structures and data](#structures-and-data)
- [Quantifiers and aggregates](#quantifiers-and-aggregates)
- [Arithmetic](#arithmetic)
- [Performance](#performance)
- [Procedures and the Python side](#procedures-and-the-python-side)

## Parsing and declarations

- **Type ranges must be integer literals.** `type Row := {1..n()}` in a vocabulary and
  `Row := {1..n}.` in a structure are both "Expected IDPFLOAT or INT". Compute the size in
  your program and write the literal.
- **Mind the element count of a range**: `{0..6}` has 7 elements and `{1..6}` has 6; a
  0-based list of n elements is `{0..n-1}`, computed in the program.
- **A type with no range is not numeric.** `type T` (no `<: Int`) cannot take part in
  arithmetic even when the structure interprets it with integers: "ℤ value expected (Row
  found: queens(r1))". Write `type T <: Int` and interpret it as `T := {1..6}.`.
- **A literal range in the vocabulary is numeric**: `type Digit := {0..9}` takes part in
  arithmetic and comparisons (`d() + 1 = 3` and `! x in Digit: d(x) + 1 =< 9` both work).
  `type Digit <: Int` with `Digit := {0..9}.` in a structure works too. Only the bare
  `type T` above is not numeric.
- **Operator precedence**, loosest to tightest: quantifiers, `<=` (reverse implication),
  `<=>`, `=>`, `|`, `&`, comparisons, `+ -`, `* / %`, unary `- ~`. Checked:
  `p() | q() & r()` with p true, q and r false is satisfiable (`&` binds first), and
  `a() & b() => c()` with a false, b true, c false is satisfiable (`(a & b) => c`). Write
  parentheses for any mix of `&`, `|` and `=>`, and for any chain of `=>`.
- **`<=` is reverse implication**, not less-or-equal: `x() <= 2.` fails with "𝔹 value
  expected (ℤ found: 2)". Write `=<`. `!=`, `==` and a missing final `.` are parse errors.
- **Write a two-argument symbol as `A * B -> Bool`**; `A -> B -> Bool` does not parse.
- **`abs` is a built-in symbol** and cannot be redeclared (it fails with an unhelpful
  `IndexError: list index out of range`). The other built-ins are `relevant`,
  `goal_symbol`, `Concept`, `true`, `false`. Other names are permissive: `a`, `S`, `T`,
  `V`, `min`, `sum`, `type`, `minimize` and uppercase names all work as symbols.
- **A symbol name must be unique**: "Duplicate declaration of D" when two symbols share
  a name. A quantified variable may not reuse a declared symbol's name either.
- `$` is FO(.) syntax only as `$( expr )` (a symbol computed from an expression).
- Python's `and`/`or`/`not` work as connectives; `abs()` works as a function.
- **For a 0/1 integer use `type Bit := {0..1}`**, not `-> Bool`, when the value is read
  as a number.

## Structures and data

- 2-D maps need tuple parentheses, `cost := {(0,0)->1, (0,1)->2}.`; bare `0,0->1` is a
  parse error. Negative values are fine.
- **A predicate takes the set of its true tuples**: `flag := {0, 1}.` or `{}`.
  `{0->true}` fails with "Can't use function enumeration for predicates 'flag' (yet)". A
  proposition takes `p := true.`.
- **0/1 integers in your data are integers**: interpret them with an `-> Int` function
  and compare with `= 1`, or turn them into the set of indices holding 1 for a predicate.
- **Ground facts in a theory do not close a predicate**: `knows(0,3).` leaves every
  unlisted pair free. State facts in a structure, or inside a definition,
  `{ knows(0,3). ... }`, so everything else is false.
- **Ragged lists**: pad to the longest row and add a length function (`F_len: I -> Int`,
  read `F(i, j)` only for `j < F_len(i)`, since padding can equal a real value), or turn
  the rows into a predicate of `(row, item)` pairs.
- **Strings** cannot be interpreted as integers: map them to integer ids in your
  program and keep the names there for printing.
- **1-based data** (coordinates, ids) with 0-based types: shift in the constraint
  (`r + 1 = lt(k, 0)`) rather than rewriting the data.
- Several structure blocks merge into one `Theory`.

## Quantifiers and aggregates

- **The comma is required**: `! a, b in T:`, not `! a b in T:`.
- **`?=n x in T:` under an implication or inside parentheses crashes** with an internal
  `TypeError` in annotation. Write the quantifier at the top of a sentence, or use a
  count `#{x in T: ...} = n`.
- **`?=<k` takes one variable**; for pairs write `#{ i, j in T: i < j & p(i, j) } =< k`.
- **Two-variable quantifiers under an implication** (`!` or `?`) fail with "set expected
  at most 1 argument"; nest them (`! r in R: ! c in C: ...`).
- **Definitions need a head quantifier**: `{ ! x, y in T: rel(x, y) <- ... }`.
- **`sum{{ }}` has double braces**; single-brace `sum{` is a parse error.
- **Parenthesise a compound term inside an aggregate** (a product, or a sum such as
  `(start(j) + dur(j))` in `max{ }`): `sum{{ a(x) * b(x) | x in T }}` fails with
  "Expected 'is\s+enumerated' or 'in|∈' or ',' or '}}' or '|'"; write
  `sum{{ (a(x) * b(x)) | x in T }}`, or define `c(x) = a(x) * b(x)` and sum `c`.
- **Counts and sums over several variables parse** (`#{ i, j in T: ... }`,
  `sum{{ cost(t, p) | t in Task, p in Person: x(t, p) }}`), but an `if ... then ... else`
  directly inside a two-variable `sum{{ }}` does not; define it as a helper symbol and
  sum that.

- **Counting a defined predicate**: put the predicate in a closed-world definition and count
  it, `{ ! c in Colour: used(c) <- ? v in Node: colour(v) = c. }` then
  `n() = #{ c in Colour: used(c) }.`. Checked: the count follows the colours the models use,
  and `optimize` on `n()` works.

## Arithmetic

- **Integer division and modulo are not consistent.** IDP-Z3 folds constants, including
  data from a structure, in Python, but sends anything involving a decision symbol to z3.
  They disagree for a **negative divisor**: `7 / -2 = -4` and `7 % -2 = -1`, yet with
  `x() = 7`, `x() / -2 = -3` and `x() % -2 = 1`; with `a := 7. b := -2.` in a structure,
  `a() / b() = -4`. For positive divisors both agree (`-7 / 2 = -4`). Avoid negative
  divisors, or constrain quotient and remainder yourself.
- **Dividing by a symbol needs a guard IDP-Z3 can see statically**: `x() / y()` fails
  with "Domain error: ¬(y() = 0) is not a tautology. Please add appropriate guards." even
  if the theory says `y() = 2`. Write `y() ~= 0 => c() = x() / y().`, use
  `if y() ~= 0 then x() / y() else 0`, or give `y` a type without 0. `%` by a symbol has
  no such check.
- The same "Domain error ... is not a tautology" appears for `p - 1` landing outside a
  type; quantify over a type one shorter instead (see adjacent pairs below).

## Performance

- **Give each decision a finite type.** Ten pairwise different values in 1..9 declared
  `-> Int` with bound constraints ran into a 60 s limit as `unknown`; the same with
  `type Val := {1..9}` proved unsatisfiable in 3.5 s.
- **Bound every integer you read back, cheaply.** An unbounded `-> Int` admits values the
  problem rules out (negative ages, entries above n). Use a small range type (up to a few
  hundred values) or explicit bounds in the theory (`0 =< x() & x() =< 50.`). Large range
  types (thousands of values), and range types on the objective or on values fixed by
  equations, make z3 slow or run out of memory: keep those `-> Int`.
- **Nonlinear integer arithmetic** (a product of two decision symbols) can make z3 run
  until its time limit, or fail to prove an optimum. Rewrite a product linearly: for ±1
  values count equal pairs instead of multiplying; for `p * x` with `x` in a small type
  write `sum{{ (if x = k then k * p else 0) | k in K }}` or a table of ground
  implications (`x() = k => y() = k * k`). A product of a decision and data is linear.
- **Large quantifier spans ground to huge theories.** Pairwise sentences over 1000
  elements ran out of memory; quantify over adjacent pairs (`! p in Adj: ... p + 1`) over
  a type one shorter. A successor rule as an existential (`x(c) ~= last => ? c2: x(c2) =
  x(c) + 1 & adjacent(c, c2)`) or an inverse map from values to cells is much faster
  than a four-variable universal implication.
- **`min{ }`/`max{ }` over a set that depends on decisions** makes optimum proofs slow;
  use Boolean presence predicates (`started(p, s) <=> ? t in T: t =< s & plays(p, t)`),
  or bound the objective from each element (`! j in Job: end(j) =< makespan().`).
- **`%` or comparisons between two decision sums are slow**: compare each sum with a
  constant computed in your program, and fold `%` over data into counts.
- Grounding is cheap for data of moderate size: a structure with a 1000-entry list
  parses in 0.36 s, `Theory()` takes 0.29 s and a z3 check 0.22 s; a 60x9 table parses in
  0.42 s.

## Procedures and the Python side

- **f-strings halve braces**: an FO(.) text built with `f"..."` turns `sum{{` into
  `sum{` and fails with "Expected '{{' ...". Keep the vocabulary and theory in a plain
  string (or use `%` formatting) and format only the generated structure.
- **Values are always truthy**: `model["p()"].value` is an Expression, and `bool()` of
  `false` is `True`. Compare `str(value) == "true"`; read integers with
  `int(str(value))`.
- `procedure` blocks run only through `IDP.execute()` or the `idp-engine` command, never
  when parsing or solving from Python. Inside one, RestrictedPython rejects `import os`
  (and every import). Strings in a procedure are double-quoted with no escapes, so they
  can never contain `"`: `print('x')` and `print("{\"a\"}")` are parse errors. A `for`
  loop in a procedure failed to parse in testing; loop in Python instead.
- **`complete=False` leaves unconstrained symbols out**: a Boolean that no sentence mentions
  reads back as `None` in every model, and its values are not enumerated. Pass
  `theory.expand(..., complete=True)` so every symbol gets a value and each value combination
  counts as a model.
- The `idp-engine` command needs `procedure main()`; without it, `KeyError: 'main'`.
