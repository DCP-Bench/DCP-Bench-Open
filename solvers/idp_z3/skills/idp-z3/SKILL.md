---
name: idp-z3
description: IDP-Z3, a reasoning engine for FO(.) ("FO-dot") knowledge bases (vocabulary, theory, structure) built on Z3; pip package idp-engine, Python module idp_engine, command idp-engine. Use when writing, debugging or explaining FO(.) models, model expansion or optimisation with IDP-Z3, or when the user has chosen IDP-Z3 for a constraint, configuration or scheduling problem.
license: Apache-2.0
compatibility: Requires Python 3.11+ on x86_64 Linux with glibc 2.28+ (the sli-lib dependency ships only as a manylinux_2_28 wheel) and pip install idp-engine; tested with idp-engine 0.12.1, which pins z3-solver 4.11.2.0. LGPL-3.0, no licence key or size limit.
metadata:
  domain: constraint-programming
  solver: idp-z3
  paradigm: smt
---

# IDP-Z3 (FO(.))

IDP-Z3 reasons over a **knowledge base** written in FO(.), typed first-order logic with
aggregates and inductive definitions: a `vocabulary` declares types and symbols, a
`theory` states sentences, a `structure` gives the data. It is not a program: you ask the
engine for models (model expansion), an optimum, or consequences, from Python
(`idp_engine`) or from a `procedure main()` run by the `idp-engine` command. The one idea
to keep in mind: **type ranges are integer literals**, so the data, sizes included, goes
into a structure that your program writes.

## Contents
- [Install](#install) · [Quick start](#quick-start) · [Knowledge base](#knowledge-base) · [FO(.) syntax](#fo-syntax)
- [Solving](#solving) · [All solutions](#all-solutions) · [Common issues](#common-issues) · [Further reading](#further-reading)
- References: [FO(.) gotchas and modelling lessons](references/gotchas.md), [engine behaviour, driving z3 directly, timings](references/engine.md)
- Examples:

| Example | Pattern | Run |
|---|---|---|
| [queens-cli](assets/queens-cli/README.md) | satisfy and all solutions, `idp-engine` command | `idp-engine --no-timing queens.idp` |
| [subset-sum-all](assets/subset-sum-all/README.md) | all solutions, Python API, auxiliary symbol | `python model.py` |
| [assignment-all-optimal](assets/assignment-all-optimal/README.md) | all optimal solutions | `python model.py` |
| [project-selection-json](assets/project-selection-json/README.md) | maximise, data from a JSON file, ragged list | `python model.py data.json` |
| [coins-minimise](assets/coins-minimise/README.md) | minimise, `idp-engine` command | `idp-engine --no-timing coins.idp` |
| [infeasible-roster](assets/infeasible-roster/README.md) | infeasible | `python model.py` |
| [schedule-makespan](assets/schedule-makespan/README.md) | scheduling, optimum under a time limit | `python model.py` |

## Install

```bash
pip install idp-engine
idp-engine --version          # 0.12.1
```

It installs its own z3-solver (4.11.2.0 for idp-engine 0.12.1, older than the current
z3), so use a virtual environment if another package needs a newer z3. Details:
[IDP-Z3 documentation](https://docs.idp-z3.be/en/stable/IDP-Z3.html)

## Quick start

```python
from idp_engine import IDP, Theory

n = 8
kb = IDP.from_str("""
vocabulary V {
    type Row <: Int
    queen: Row -> Row                       // queen(r) = column of the queen in row r
}
theory T: V {
    // different columns and diagonals
    ! r1, r2 in Row: r1 < r2 => queen(r1) ~= queen(r2).
    ! r1, r2 in Row: r1 < r2 => queen(r1) - r1 ~= queen(r2) - r2.
    ! r1, r2 in Row: r1 < r2 => queen(r1) + r1 ~= queen(r2) + r2.
}
structure S: V {
    Row := {1..%d}.
}
""" % n)
theory = Theory(*kb.get_blocks("T, S"))
for model in theory.expand(max=1, timeout_seconds=10):
    if isinstance(model, str):
        print(model.strip())        # "No models." when infeasible
    else:
        print([int(str(model[f"queen({r})"].value)) for r in range(1, n + 1)])
```

## Knowledge base

Language reference: [FO(.)](https://docs.idp-z3.be/en/stable/FO-dot.html) · [syntax summary](https://docs.idp-z3.be/en/stable/summary.html)

| Need | Write |
|---|---|
| index type sized by data | vocabulary `type Item <: Int`, structure `Item := {0..4}.` (`{}` when empty) |
| fixed small range | `type Digit := {0..9}` in the vocabulary: a literal range is numeric, so `d() + 1 = 3` works. Literals only: `{1..n()}` is a parse error |
| integer decision | function into a finite type, `val: Letter -> Digit` |
| yes/no decision | predicate, `queen: Row * Col -> Bool` (never `Row -> Col -> Bool`) |
| constant | `n: () -> Int`, used as `n()` (always applied) |
| 1-D / 2-D data | `w := {0->7, 1->8}.` / `cost := {(0,0)->1, (0,1)->2}.` (tuple parentheses required) |
| predicate data | the set of true tuples, `edge := {(0,1), (1,2)}.` or `{}` |
| proposition data | `p := true.` |
| definition (closed world) | `{ ! x in T: reach(x) <- start(x). ! x in T: reach(x) <- ? y in T: reach(y) & edge(y, x). }` |
| count of a defined predicate | `{ ! c in Colour: used(c) <- ? v in Node: colour(v) = c. }` then `n() = #{ c in Colour: used(c) }.` |
| objective | a nullary `total: () -> Int` fixed by `total() = sum{{ ... }}.` |

Write the knowledge base as a plain string and **append a structure generated from your
data** ([project-selection-json](assets/project-selection-json/README.md)): sizes become
range literals, lists become `{i->v}` maps, ragged lists become predicates or a padded
map with a length function. Compute any constant the theory needs (a magic sum, a bound)
in the program and put it in the structure. Several structure blocks merge into one
`Theory`. Arrays you write 0-based stay 0-based; shift 1-based data in the constraint
(`r + 1 = pos(k)`). Comment each block of sentences with the requirement it encodes.

## FO(.) syntax

| Meaning | Write | Not |
|---|---|---|
| less-or-equal | `=<` | `<=` (reverse implication) |
| not equal / equal | `~=` / `=` | `!=` / `==` (parse errors) |
| and / or / not | `&` `\|` `~` (or `and` `or` `not`) | |
| implies / iff | `=>` / `<=>` | |
| for all / exists | `! a, b in T:` / `? a in T:` | `! a b in T:` (comma required) |
| exactly / at most / at least k | `?=1 v in T: p(v).` `?=<2 ...` `?>=2 ...` | |
| count | `#{ v in T: p(v) }` | |
| sum | `sum{{ e(v) \| v in T: guard(v) }}` (**double** braces) | `sum{ ... }`, `sum(v in T)(e)` |
| min / max | `max{ e(v) \| v in T: guard(v) }` | |
| conditional term | `if c then a else b` | |
| definition | `{ ! v in T: even(v) <- v % 2 = 0. }` | |

**Every sentence ends with `.`**. Declarations are `name: A * B -> Result`; there is no
`var`/`pred` keyword. The parser's useful line is the **last** one,
`Expected ... at position (l, c) => '... *token ...'`, where `*` marks where it stopped.
**Precedence**, loosest to tightest: quantifiers, `<=`, `<=>`, `=>`, `|`, `&`, comparisons,
`+ -`, `* / %`, unary `- ~`. So `a & b => c` means `(a & b) => c`, and `p | q & r` means
`p | (q & r)` (both checked). Parenthesise any sentence that mixes `&`, `|` and `=>`, and
any chain of `=>`, so the reader does not have to apply the table.

The full list of traps, each verified: [references/gotchas.md](references/gotchas.md).

## Solving

API: [IDP-Z3 Python API and procedures](https://docs.idp-z3.be/en/stable/IDP-Z3.html)

| Call | Does |
|---|---|
| `IDP.from_str(text)` / `IDP.from_file(path)` | parse; uninterpreted `<: Int` types are fine until `Theory()` |
| `kb.get_blocks("T, S")` | the named blocks (default names `V`, `T`, `S`) |
| `Theory(*blocks)` | ground; "Expected an interpretation for type X" if a type is unsized |
| `theory.expand(max=10, timeout_seconds=10, complete=False)` | yields models (`Assignments`), then **one message string**; `max=0`, `timeout_seconds=0` mean unlimited |
| `theory.optimize("total()", minimize=True)` | fixes `total()` to its optimum; chain `.expand()` for the models |
| `model["queen(3)"].value` | an Expression; keys look like `"cost(0, 1)"`, `"total()"` |

Messages: `"No models."` (infeasible), `"\nNo more models."` (enumeration complete),
`"\nMore models may be available.  Change the max argument to see them."`, the
`timeout_seconds` variants, and `"\nNo model found in N seconds. ..."`.

- **Read values by text**: `int(str(v.value))`; a Boolean is `str(v.value) == "true"`.
  `bool(v.value)` is always `True`, even for `false`. With `complete=False` (the default) an
  unconstrained term's value can be `None` and is not enumerated; pass `complete=True` when
  every symbol needs a value ([gotchas](references/gotchas.md#procedures-and-the-python-side)).
- `optimize` raises `AssertionError("Optimization requires satisfiable specification")` for
  an infeasible theory **and** when z3 gives up, has **no time limit**, and returns a wrong
  optimum for an unbounded objective. Give the objective's ingredients finite types, or
  drive the z3 `Optimize` yourself ([schedule-makespan](assets/schedule-makespan/README.md),
  [references/engine.md](references/engine.md)).
- **Command line**: `idp-engine file.idp` runs `procedure main()` (without one: `KeyError:
  'main'`), with `pretty_print(model_expand(T, S, max=0, timeout_seconds=0))`,
  `pretty_print(minimize(T, S, term="total()"))` (one optimal model; `maximize` likewise),
  `model_check(T, S)` (`sat`/`unsat`), `model_propagate(T, S)`. `--no-timing` drops the
  timing line. A procedure cannot import modules, so read JSON data from Python.
- Errors are exceptions with a traceback (the CLI exits 1); the last line is the useful one.

## All solutions

`theory.expand(max=0, timeout_seconds=0)` enumerates until `"\nNo more models."`
([subset-sum-all](assets/subset-sum-all/README.md)). It blocks on **every** unknown term,
so a free auxiliary symbol multiplies the models (a free `aux: () -> V` turned 3
solutions into 9; a leading `_` does not help): fix each auxiliary symbol by an equation
or a definition. **All optimal**: `theory.optimize(...)` then `theory.expand(max=0, ...)`
enumerates only optimal models ([assignment-all-optimal](assets/assignment-all-optimal/README.md));
with the z3 route, add `term == best` to `theory.solver` and block the output terms
yourself ([references/engine.md](references/engine.md)).

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| `Expected IDPFLOAT or INT` at a type range | `{1..n()}` or `{1..n}` | write the literal from your program ([Knowledge base](#knowledge-base)) |
| `Expected '{{' ...` after `sum{` | an f-string turned `{{` into `{` | keep FO(.) in a plain string; format only the structure |
| `𝔹 value expected (ℤ found: 2)` | `x() <= 2` is reverse implication | `=<` |
| `ℤ value expected (Row found: ...)` | `type Row` with no range and no `<: Int` | `type Row <: Int`, or a literal range `type Row := {1..9}` |
| `Domain error: ¬(y() = 0) is not a tautology` | division by a symbol | guard it ([gotchas](references/gotchas.md#arithmetic)) |
| `IndexError: list index out of range` at parse | redeclared `abs` | rename it |
| `Duplicate declaration of D` | two symbols named alike | rename one |
| `set expected at most 1 argument` | two-variable quantifier under an implication | nest the quantifiers |
| `TypeError` in annotation | `?=n` under an implication or parentheses | put it at the top of a sentence, or use `#{ }` |
| `Can't use function enumeration for predicates` | `p := {0->true}.` | `p := {0}.` |
| every Boolean reads as true | `bool(value)` | `str(value) == "true"` |
| models repeat with the same decisions | a free auxiliary symbol | fix it by an equation or definition |
| an output reads back `None`, or models differ only in an unconstrained symbol | `expand` with the default `complete=False` | `complete=True`, or constrain the symbol ([engine](references/engine.md)) |
| a sentence with `&`, `\|` and `=>` means something other than intended | precedence: `&` binds tighter than `\|`, which binds tighter than `=>` | parenthesise the parts ([FO(.) syntax](#fo-syntax)) |
| slow or `unknown`, out of memory | nonlinear product, unbounded `-> Int`, huge quantifier span | [performance lessons](references/gotchas.md#performance) |
| unlisted facts are free | ground facts written in a theory | put them in a definition `{ ... }` or a structure |
| wrong "optimum" | unbounded objective | bound it; check `lower == upper` ([engine](references/engine.md)) |

## Further reading

- Documentation: <https://docs.idp-z3.be/en/stable/> (FO(.) reference, summary, Python API)
- Package: <https://pypi.org/project/idp-engine/>
- Source of truth for engine behaviour: `idp_engine/Theory.py` and the grammar `idp_engine/Idp.tx` in the installed package
