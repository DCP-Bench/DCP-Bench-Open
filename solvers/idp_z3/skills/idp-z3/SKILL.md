---
name: idp-z3
description: Write instance-agnostic FO(.) knowledge bases for the DCP-Bench idp_z3 integration (IDP-Z3 0.12.1), covering how instance data reaches the knowledge base through a generated structure (including types sized by a scalar field), the minimize/maximize objective convention, FO(.) syntax that differs from every other modelling language, and the arithmetic and parsing traps that make a submission fail.
---

# FO(.) knowledge bases for `idp_z3`

A submission is a plain FO(.) ("FO-dot") file — a `vocabulary` and a `theory`,
nothing else needed. It is **not a program**: you never call anything, and the
runner never executes code from your file (a `procedure` block is ignored).
IDP-Z3 parses the file exactly as written. The runner hands the instance in as a
`structure` over your vocabulary, asks IDP-Z3 for models, and prints them.

Image: idp-engine 0.12.1 (which pins z3-solver 4.11.2.0) on Python 3.12.

## The contract

```
vocabulary {
    type Range_n <: Int            // the runner interprets it as {1..n}
    queens: Range_n -> Range_n     // a declared output: one value per row
}
theory {
    ! r1, r2 in Range_n: r1 ~= r2 => queens(r1) ~= queens(r2).
    ! r1, r2 in Range_n: r1 ~= r2 => queens(r1) - r1 ~= queens(r2) - r2.
    ! r1, r2 in Range_n: r1 ~= r2 => queens(r1) + r1 ~= queens(r2) + r2.
}
```

- **Declared outputs are symbols with exactly the reference's output names.**
  `queens: Row -> Row` is read back as a list ordered by `Row` ascending; a
  two-argument symbol becomes a list of lists (first argument outermost); a
  nullary `z: () -> Int` or `p: () -> Bool` becomes a scalar. A `-> Bool`
  symbol reads back as `true`/`false`, an integer one as an integer. Every
  output must be total over its argument types.
- **Optimization**: declare a nullary integer `minimize: () -> Int` *or*
  `maximize: () -> Int` and define it in the theory
  (`minimize() = sum{{ cost(t, p) | t in Task, p in Person: x(t, p) }}.`).
  No such symbol means a satisfaction problem. The runner proves the optimum
  itself and reports an unbounded objective as an error, never as a value.
- Name extra symbols however you like — auxiliary symbols are fine, and do not
  multiply the solutions the runner enumerates (it compares declared outputs
  only).

**Take every quantity from the instance.** A model that hardcodes the numbers of
the example is the one failure this benchmark exists to catch, and it will be
rejected the moment a second instance is checked.

## How the instance gets in

In FO(.), data is handed to a knowledge base in a `structure` block. You do not
write it: the runner generates one per instance, `structure _dcp_instance:V { ... }`,
interpreting the symbols and types your vocabulary declares. The instance JSON
never appears in your file. FO(.) type ranges must be integer literals
(`type Row := {1..n()}` is a parse error), which is why the structure also
interprets the types the data sizes. Three rules:

1. **A symbol with the same name as an instance field is interpreted from it.**

   | Instance field | Declare | Runner writes |
   | --- | --- | --- |
   | `n: 5` | `n: () -> Int` | `n := 5.` |
   | `w: [7, 8]` | `type I <: Int` and `w: I -> Int` | `w := {0->7, 1->8}.` and `I := {0..1}.` |
   | `cost: [[..],[..]]` (2x3) | `cost: Task * Person -> Int` | `cost := {(0,0)->.., ...}.`, `Task := {0..1}.`, `Person := {0..2}.` |
   | `flag: [true, false]` | `flag: I -> Bool` | `flag := {0}.` (the set of true indices) |
   | `p: true` | `p: () -> Bool` | `p := true.` |
   | `F: [[1, 2, 3], [4]]` (ragged rows) | `type I <: Int`, `type J <: Int`, `F: I * J -> Int`, `F_len: I -> Int` | `F := {(0,0)->1, ..., (1,0)->4, (1,1)->0, (1,2)->0}`, `J := {0..2}`, `F_len := {0->3, 1->1}` (`F_len` only if declared) |
   | `R: [[7, [1, 1], [1, 2]], [9, [2, 2]]]` (rows of `[target, cells...]`) | `R_1: I -> Int`, `R_2: I * J * K -> Int`, `R_2_len: I -> Int` | `R_1 := {0->7, 1->9}`; `R_2` holds the padded cells, `R` itself is not bound |

   A ragged list of rows pads with 0 (false for Booleans), so the model reads
   `F(i, j)` only for `j` below `F_len(i)`. Mixed rows split into `F_1`, `F_2`, ...
   by column when all rows have one length, or into a scalar head and a ragged tail
   otherwise. Only the names the model declares are bound; strings and floats are
   refused only in a declared field.

2. **An array sizes its index types.** Array indices are **0-based**, like the
   JSON. An argument type is sized from the data only when you declare it
   `type T <: Int` with no range of your own; if two fields would size the same
   type differently, that is an error. A field you do not declare is ignored.

3. **`type Range_f <: Int` is `{1..f}` for an integer scalar field `f`.** With
   `n: 8`, `type Range_n <: Int` becomes `Range_n := {1..8}.`, and
   `type Range_days <: Int` is `{1..days}`. A `Range_` type naming a field that is
   not an integer scalar is an error, and a `Range_` type cannot index an instance
   array (arrays index from 0; declare a separate `type I <: Int` for that).

Values derived from the data belong in the theory, written with the data
constants: `n() * (n() * n() + 1) / 2`, `2 * k()`. IDP-Z3 folds these before
solving, so they cost nothing.

```
vocabulary {
    type I <: Int                  // sized from npv's length
    budget: () -> Int
    npv: I -> Int
    cash_flow: I -> Int
    x: I -> Bool                   // declared output
    z: () -> Int                   // declared output
    maximize: () -> Int
}
theory {
    sum{{ cash_flow(i) | i in I: x(i) }} =< budget().
    z() = sum{{ npv(i) | i in I: x(i) }}.
    maximize() = z().
}
```

## FO(.) syntax — what differs from everything else

| Meaning | Write | Not |
| --- | --- | --- |
| less-or-equal | `=<` | `<=` (that is reverse implication) |
| not equal / equal | `~=` / `=` | `!=` / `==` (parse errors) |
| and / or / not | `&` `\|` `~` (or `and` `or` `not`) | |
| implies / iff | `=>` / `<=>` | |
| for all / exists | `! a, b in T:` / `? a in T:` | `! a b in T:` (the comma is required) |
| exactly / at most / at least k | `?=1 v in T: p(v).` `?=<2 ...` `?>=2 ...` | |
| count | `#{ v in T: p(v) }` | |
| sum | `sum{{ e(v) \| v in T: guard(v) }}` — **double** braces | `sum{ ... }`, `sum(v in T)(e)` |
| min / max | `max{ e(v) \| v in T: guard(v) }` | |
| conditional term | `if c then a else b` | |
| definition | `{ ! v in T: even(v) <- v % 2 = 0. }` | |
| constant | `n()` — always applied | bare `n` |

- **Every sentence ends with `.`** — a missing period is a parse error.
- **Comment each block of sentences** with a `//` line taken from the problem
  description (e.g. `// every row holds different values`), so the theory can be
  read against the statement.
- Declarations are `name: Arg1 * Arg2 -> Result`; there is no `pred`/`var`
  keyword. Integer decisions are functions (`val: Letter -> Digit`), yes/no
  facts are predicates (`queen: Row * Col -> Bool`).
- The parser's useful line is the last one, `Expected ... at position (l, c)
  => '... *token ...'`; the `*` marks where it stopped. Ignore the stack above.

## Gotchas, all verified against IDP-Z3 0.12.1

- **Integer division and modulo are not consistent.** IDP-Z3 folds constants —
  including instance data, which arrives as constants — in Python, but sends
  anything involving a decision symbol to z3. They disagree for a **negative
  divisor**: `7 / -2 = -4` and `7 % -2 = -1`, yet with `x() = 7`,
  `x() / -2 = -3` and `x() % -2 = 1`. For positive divisors both agree
  (`-7 / 2 = -4`). Avoid negative divisors, or constrain quotient and
  remainder yourself.
- **Dividing by a symbol needs a guard IDP-Z3 can see statically**: `x() / y()`
  fails with "Domain error: ¬(y() = 0) is not a tautology" even if the theory
  says `y() = 2`. Write `y() ~= 0 => c() = x() / y().`, use
  `if y() ~= 0 then x() / y() else 0`, or give `y` a type without 0.
- **A type with no range is not numeric.** `type T` (no `<: Int`) cannot take
  part in arithmetic even if it is interpreted with integers; write
  `type T <: Int` for an index type the runner should size.
- **`abs` is a built-in symbol** and cannot be redeclared (it fails with an
  unhelpful `IndexError`). Other names are permissive: `a`, `S`, `T`, `V`,
  `min`, `sum`, uppercase names all work as symbols.
- **Other ranges are built from `Range_f` and array index types in FO(.):**
  - `0..n-1`: quantify over `Range_n` and write `r - 1`, or index by a 0-based
    array type when one exists (`type I <: Int` with `w: I -> Int` is `{0..len-1}`).
  - `0..n` (a count that may be 0): declare `-> Int` and bound it in the theory,
    `0 =< c(i) & c(i) =< n().`
  - `1..2*k`, `1..n*n`, `1..sum(demand)`: use pairs of smaller types
    (`cell: Range_n * Range_n -> Bool` for an n x n grid), or `-> Int` with bounds
    from the data (`0 =< start(j) & start(j) =< sum{{ demand(i) | i in I }}.`).
- Integer division in a theory is `/`; `//` starts a comment.
- **`?=n x in T:` under an implication or parentheses crashes idp-engine 0.12.1**
  (an internal `TypeError` in annotation, reported as an `error` status). Write
  the quantifier at the top of a sentence, or use `#{x in T: ...}` counts.
- **Interpreting a data symbol yourself (in your own `structure`) stops the
  runner from binding it** — the instance value is then ignored, which is
  exactly the hardcoding the evaluator rejects on the next instance.
- **Nonlinear integer arithmetic** (a product of two decision symbols) can make
  z3 run until the budget is spent, or fail to prove an optimum. Rewrite a
  product linearly: for ±1 values count equal pairs instead of multiplying; for
  `p * x` with `x` in a small type write `sum{{ (if x = k then k * p else 0) | k in K }}`
  or a table of ground implications (`x() = k => y() = k * k`).
- **An unbounded `-> Int` decision makes hard cases time out.** Ten pairwise
  different values in 1..9 declared `-> Int` with bound constraints ran into the
  60 s limit as `unknown`; the same with `type Val := {1..9}` proved
  unsatisfiable in 3.5 s. Give each decision a finite type.
- **Parenthesise a compound term inside an aggregate** (a product, or a sum such as
  `(start(j) + dur(j))` in `max{ }`): `sum{{ a(x) * b(x) | x in T }}` fails
  with "Expected 'is\s+enumerated' or 'in|∈' or ',' or '}}' or '|'"; write
  `sum{{ (a(x) * b(x)) | x in T }}`, or define `c(x) = a(x) * b(x)` and sum `c`.
- **An output's argument type sets its length**: a list of n values is a symbol
  over `Range_n`, or over an array's index type when the list follows an array.
- **Bound every output, cheaply.** An unbounded `-> Int` output admits values the
  description rules out (negative ages, entries above n), and the evaluator
  rejects them with "Declared outputs cannot extend to a reference solution".
  Use a small range type (up to a few hundred values) or explicit bounds in the
  theory on a `-> Int` output (`0 =< x() & x() =< max_val().`). Large range
  types (thousands of values) and range types on the objective or on values
  fixed by equations make z3 slow or run out of memory; keep those `-> Int`.
- **An output the brief shows as `int` must not be `-> Bool`**: the evaluator
  says "Expected integer at x[0][0]". Use `type Bit := {0..1}`.
- **Ground facts in a theory do not close a predicate**: `knows(0,3).` leaves
  every unlisted pair free. State facts inside a definition, `{ knows(0,3). ... }`,
  so everything else is false.
- **Write a two-argument symbol as `A * B -> Bool`**; `A -> B -> Bool` does not parse.
- **`?=<k` takes one variable**; for pairs write `#{ i, j in T: i < j & p(i, j) } =< k`.
- **Counts and sums over several variables parse** (`#{ i, j in T: ... }`), but an
  `if ... then ... else` directly inside a two-variable `sum{{ }}` does not; define
  it as a helper symbol and sum that.
- **`min{ }`/`max{ }` over a set that depends on decisions** makes optimum proofs
  slow; use Boolean presence predicates (`started(p, s) <=> ? t in T: t =< s & plays(p, t)`).
- **A symbol name must be unique**: "Duplicate declaration of D" when an output
  and a helper share a name.
- **String fields cannot be bound**: declaring one fails with "instance values of
  type str cannot be bound"; an undeclared string field or column is ignored, so
  bind only the integer columns of a mixed row (`movies_2`, `movies_3`). Padding
  of ragged rows is 0, so compare 1-based ids or guard with `F_len`.
- **A data field holding 0/1 integers binds as `-> Int`**; compare it with `= 1`.
  Declared `-> Bool` it fails with "Declared outputs cannot extend ..." without
  naming the field.
- **Large quantifier spans ground to huge theories.** Pairwise sentences over 1000
  elements ran out of memory; quantify over adjacent pairs (`! p in Adj: ... p + 1`)
  over a type one shorter, which also avoids "Domain error ... is not a tautology"
  on `p - 1`. A successor rule as an existential (`x(c) ~= last => ? c2: x(c2) =
  x(c) + 1 & adjacent(c, c2)`) or an inverse map from values to cells is much
  faster than a four-variable universal implication.
- **`%` or comparisons between two decision sums are slow**: compare each sum
  with a constant written from data symbols, and fold `%` over data into counts.
- **Two-variable quantifiers under an implication** (`!` or `?`) fail with "set
  expected at most 1 argument"; nest them (`! r in R: ! c in C: ...`). A quantified
  variable may not reuse a declared symbol's name. Definitions need a
  head quantifier: `{ ! x, y in T: rel(x, y) <- ... }`.
- **Instance coordinates may be 1-based** while arrays bind 0-based; shift in
  the constraint (`r + 1 = lt(k, 0)`) rather than in the data.

## Check your own model before submitting

```sh
python -m evaluation.check MODEL.idp --problem PROBLEM --solver idp_z3 --instance-count 99
```

`--instance-count 99` checks every instance the problem has, which is what
catches a model that fitted the example. `python -m generation.brief PROBLEM`
lists the declared output names and every instance field with its shape.

Read `reason` and `detail` on failure. `execution_error` covers everything the
runner rejects before solving: a parse or type error (the detail names the line
and column), a declared output that is not a symbol ("Declared output huey is
not a symbol of the vocabulary"), a `Range_` type with no matching field, or data that does not fit its
declaration. `invalid_solution` means the reference rejects a solution your
theory allows, `suboptimal_solution` means the objective is wrong,
`invalid_output` means an output came back with the wrong shape or type, and
`execution_timeout` usually means nonlinear arithmetic or a type left far
larger than the problem needs.

Repair the model from the reported reason. Never change the reference, the
dataset, or the evaluator to make a submission pass.
