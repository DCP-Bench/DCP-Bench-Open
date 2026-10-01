---
name: idp-z3
description: Write instance-agnostic FO(.) knowledge bases for the DCP-Bench idp_z3 integration (IDP-Z3 0.12.1), covering how instance data is bound into the vocabulary, the ${name} placeholder for type ranges, the minimize/maximize objective convention, FO(.) syntax that differs from every other modelling language, and the arithmetic and parsing traps that make a submission fail.
---

# FO(.) knowledge bases for `idp_z3`

A submission is a plain FO(.) ("FO-dot") file — a `vocabulary` and a `theory`,
nothing else needed. It is **not a program**: you never call anything, and the
runner never executes code from your file (a `procedure` block is ignored).
The runner binds the instance into your vocabulary, asks IDP-Z3 for models, and
prints them.

Image: idp-engine 0.12.1 (which pins z3-solver 4.11.2.0) on Python 3.12.

## The contract

```
vocabulary {
    type Row := {1..${n}}          // ${n} is replaced by the instance's integer n
    queens: Row -> Row             // a declared output: one value per Row
}
theory {
    ! r1, r2 in Row: r1 ~= r2 => queens(r1) ~= queens(r2).
    ! r1, r2 in Row: r1 ~= r2 => queens(r1) - r1 ~= queens(r2) - r2.
    ! r1, r2 in Row: r1 ~= r2 => queens(r1) + r1 ~= queens(r2) + r2.
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

FO(.) type ranges must be integer *literals* — `type Row := {1..n()}` is a
parse error — so the runner provides two mechanisms:

1. **`${name}`** anywhere in the file is replaced by the instance's integer
   scalar field `name` before parsing. Use it for type ranges:
   `type Row := {1..${n}}`, `type Day := {0..${days}}`. Only integer scalars;
   anything else is an error naming the field.
2. **Declare a symbol with the same name as an instance field and the runner
   interprets it** in a generated structure:

   | Instance field | Declare | Runner writes |
   | --- | --- | --- |
   | `n: 5` | `n: () -> Int` | `n := 5.` |
   | `w: [7, 8]` | `type I <: Int` and `w: I -> Int` | `w := {0->7, 1->8}.` and `I := {0..1}.` |
   | `cost: [[..],[..]]` (2x3) | `cost: Task * Person -> Int` | `cost := {(0,0)->.., ...}.`, `Task := {0..1}.`, `Person := {0..2}.` |
   | `flag: [true, false]` | `flag: I -> Bool` | `flag := {0}.` (the set of true indices) |
   | `p: true` | `p: () -> Bool` | `p := true.` |

   Array indices are **0-based**, like the JSON. An argument type is sized
   from the data only when you declare it `type T <: Int` with no range of
   your own; if two fields would size the same type differently, that is an
   error. A field you do not declare is ignored. String fields cannot be bound.

The two compose: size the index type from data, and use `${n}` for ranges that
come from a scalar.

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
- **`${...}` only takes a field name**, not an expression: `${n}` works,
  `${n-1}` is rejected with "a placeholder takes one integer field name". Write
  `{0..${n}}` and adjust the theory, or size the type from an array instead.
- **Interpreting a data symbol yourself (in your own `structure`) stops the
  runner from binding it** — the instance value is then ignored, which is
  exactly the hardcoding the evaluator rejects on the next instance.
- **Nonlinear integer arithmetic** (a product of two decision symbols) can make
  z3 run until the budget is spent; it is reported as a timeout, never as "no
  solution". Prefer a finite type for every decision.

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
not a symbol of the vocabulary"), a bad `${...}`, or data that does not fit its
declaration. `invalid_solution` means the reference rejects a solution your
theory allows, `suboptimal_solution` means the objective is wrong,
`invalid_output` means an output came back with the wrong shape or type, and
`execution_timeout` usually means nonlinear arithmetic or a type left far
larger than the problem needs.

Repair the model from the reported reason. Never change the reference, the
dataset, or the evaluator to make a submission pass.
