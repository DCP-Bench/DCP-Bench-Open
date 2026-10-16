# idp_z3: how this integration realises the submission contract

Read [the submission contract](../CONTRACT.md) first; this file only says how FO(.) on
IDP-Z3 expresses it. Runner: [run.py](run.py), self-contained (it does not use
`runner/runtime.py`, although the image carries a copy): it substitutes `${...}` sizes,
binds the instance into a generated structure, and drives z3 itself.
[metadata.yaml](metadata.yaml) declares `instance_binding: reshaped`: the runner's own
`refusal()` decides which instance fields no model can bind (see [Instance](#instance)).

## Submission file

One FO(.) knowledge base, `model.idp`: exactly one `vocabulary`, a `theory`, and
optionally a `structure` of your own. It is not a program: the runner
never calls a `procedure` or `main` block, and no other file of yours is staged.

## Entrypoint

There is no function. The runner parses the file with `IDP.from_str` and reads:

- the single vocabulary (more than one is an error: "A submission must declare exactly
  one vocabulary");
- the symbols named like the declared outputs (see [Outputs](#outputs));
- the symbols named like instance fields, which it interprets (see [Instance](#instance));
- an optional nullary `minimize: () -> Int` or `maximize: () -> Int` (see [Objective](#objective)).

Every theory and every structure in the file, plus the generated one, is combined into
one `Theory`.

## Instance

The instance enters in two ways.

**1. `${...}` size expressions.** FO(.) type ranges must be integer literals
(`type Row := {1..n()}` is a parse error), so before parsing, every `${...}` anywhere in
the source (theory and comments included) is replaced by the integer value of an
expression over the instance. Allowed: an integer scalar field `n`, integer literals,
unary `+ -`, `+ - * //`, `/` (exact division, refused unless it divides evenly; division
by zero refused), `**` with a non-negative exponent (results above 10^7 refused),
parentheses, and `sum(F)`, `len(F)`, `max(F)`, `min(F)` of one integer array field `F` of
any depth or raggedness: `len` is the number of top-level rows, and `sum`, `max`, `min` run
over every integer entry (so `max(edges)` over a list of `[u, v]` pairs works; `max`/`min`
of an empty array is refused). The expression is parsed with `ast` and evaluated by a
whitelist, never by `eval`. Anything else (another call, an attribute, a name that is not
an instance field, a Boolean or array where a scalar is needed) is refused with
`${...}: a placeholder takes an integer expression over instance fields: ...; <reason>`,
status `error`. A `$` is otherwise legal in FO(.) only directly before `(`, so the marker
cannot collide with real syntax. Wrap the whole expression: `{0..${2*n+1}}`, not
`{0..2*${n}+1}`. Inside `${...}`, `//` is Python floor division; outside it, `//` starts a
comment and integer division is `/`.

**2. Symbols named like a field.** Every instance field (or reshaped piece, below) whose
name is a symbol (function or predicate) declared in the vocabulary, and which no
`structure` of your own interprets, is interpreted in a generated
`structure _dcp_instance:<vocabulary>`. Indices are **0-based**, like the JSON:

| Instance field | Declare | Runner writes |
| --- | --- | --- |
| `n: 5` | `n: () -> Int` | `n := 5.` |
| `p: true` | `p: () -> Bool` | `p := true.` |
| `w: [7, 8]` | `type I <: Int`, `w: I -> Int` | `w := {0->7, 1->8}.`, `I := {0..1}.` |
| `cost: [[..],[..]]` (2x3) | `cost: Task * Person -> Int` | `cost := {(0,0)->.., ...}.`, `Task := {0..1}.`, `Person := {0..2}.` |
| `flag: [true, false]` | `flag: I -> Bool` | `flag := {0}.` (the set of true indices) |

- **Index types are sized from the data** only when declared `type T <: Int` with no
  range and interpreted nowhere else: axis K of the field gives `T := {0..len-1}` (`{}`
  for length 0). Two fields that would size one type differently are an error ("type T
  would be sized both 3 and 4").
- The number of argument types must equal the field's number of dimensions, else an
  error ("x is declared with 2 arguments but the instance field has 1 dimensions").
- A `-> Bool` symbol is interpreted as the set of indices whose value is JSON `true`;
  anything else in it (an integer `1`) counts as false. Bind a 0/1 integer field as
  `-> Int` and compare with `= 1`.
- A field the model does not declare is ignored, whatever its type. A symbol interpreted
  in your own `structure` is **not** bound: the instance value is ignored.

**Reshaping.** Fields FO(.) cannot interpret as they are are reshaped first (`pieces()`
in run.py):

1. A scalar, or a rectangular list of one scalar type, binds unchanged; a nonempty list
   of rows also gives `<field>_len` (each row's length).
2. A ragged list of rows whose items share one shape and one scalar type binds as
   `<field>` padded to the longest row with `0` (`false` for Booleans; rows of arrays gain
   a dimension, padded with zero blocks), plus `<field>_len`. Read `F(i, j)` only for `j`
   below `F_len(i)`: padding can equal a real value.
3. Rows of one length whose columns differ in type bind one piece per column, `<field>_1`,
   `<field>_2`, ... (numbered from 1), each by rules 1 and 2 without splitting again;
   `<field>` itself is not bound.
4. Otherwise, rows (all nonempty) whose first items are scalars of one type bind as
   `<field>_1` (the first items) and `<field>_2` (the rest of each row, by rule 1 or 2).
   `R: [[7, [1, 1], [1, 2]], [9, [2, 2]]]` gives `R_1 := {0->7, 1->9}` and `R_2` (the
   padded cells, `I * J * K -> Int`) with `R_2_len`.
5. Anything else raises `` Instance field `F` is ragged or mixes types in a way this
   integration cannot bind: only the shapes in the rules of pieces() are reshaped ``.

Each piece and each `_len` is bound only if the model declares a symbol of that name.

**Refusals.** A refusal of the data is status `unsupported` (evaluator reason
`unsupported_capability`), and happens only for a declared name:

- a declared field of rule-5 shape;
- a declared string or float value: "instance values of type str cannot be bound into
  FO(.)" (an undeclared string field or column is ignored: bind only the integer columns
  of a mixed row, such as `movies_2`, `movies_3`);
- two instance fields that bind under one declared name (`` instance fields `F` and `G`
  both bind as `F_len` ``).

**Which problems are withheld.** `generation.next_work` withholds a problem for this
integration only when run.py's `refusal(name, value)` rejects a field (other than `name`
and `note`) in some instance, i.e. a rule-5 shape no model could bind. Strings and floats
are not a shape problem and withhold nothing.

## Outputs

Each declared output is a symbol with exactly the output's name. After solving, the runner
collects the ground atoms of that symbol, evaluates each in the z3 model (with model
completion), and nests them by argument value in ascending order, first argument
outermost:

- `z: () -> Int` or `p: () -> Bool` is a scalar;
- `queens: Row -> Row` is a list ordered by `Row` ascending, whatever the range starts
  at (`{1..${n}}` gives n entries);
- `grid: R * C -> Int` is a list of lists.

`-> Bool` reads back as JSON `true`/`false`, an integer codomain as an integer; any other
value is an error ("Declared outputs must be integer or Boolean"). An output must be total
over its argument types ("A declared output must be total over its argument types"); a
name with no ground atoms is "Declared output huey is not a symbol of the vocabulary".
Other symbols are auxiliary and never reported.

## Objective

Declare a nullary integer `minimize: () -> Int` **or** `maximize: () -> Int` (a codomain
that is `Int` or a type `<: Int`) and define it in the theory
(`minimize() = sum{{ cost(t, p) | t in Task, p in Person: x(t, p) }}.`). Both, or one
with arguments or a non-integer codomain, is an error. No such symbol means a
satisfaction problem.

## Solving

The runner does not call `Theory.expand` or `Theory.optimize` (`expand` blocks on every
unknown atom, so auxiliary symbols would multiply the models, and treats z3 `unknown` as
`unsat`; `optimize` raises the same error for an unsatisfiable theory and a timeout). It
asserts the theory's assignments into `theory.solver` (a `z3.Solver`) and, for an
optimisation, `theory.optimize_solver` (a `z3.Optimize`), with z3 defaults otherwise.

- **Optimisation**: one `Optimize.check()` on the objective term. `unsat` is `unsat`; any
  other non-`sat` answer is `timeout` ("Candidate optimum was not proven"). The optimum is
  proven only when the objective's lower and upper bounds are equal finite integers;
  unequal bounds are `timeout`, and non-integer (infinite) bounds are `error` ("The
  objective is unbounded: between L and H"). The optimum is then pinned on the solver
  (`objective == best`) for enumeration.
- **Enumeration** (satisfaction, or pinned at the optimum): `check()`; on `sat`, emit the
  declared outputs and add `Or(term != value)` over every ground term of every declared
  output, so only declared outputs are blocked and auxiliary symbols never produce
  repeats. It stops at `solution_limit` (`limit`); `unsat` is exhaustion (`complete`, or
  `unsat` with nothing reported); z3 `unknown` is always `timeout`, never exhaustion.
- **Time**: the deadline is `execution_timeout` from the start of solving (after the
  request is read). Each z3 `check` gets the milliseconds left as z3's `timeout`; none
  left is `timeout`. Parsing and grounding are not under z3's limit: a `SIGALRM` at
  `execution_timeout + 5` s turns into `timeout`, and the evaluator kills the container
  at `execution_timeout + 10` s (`execution_timeout`).
- **Errors**: any other exception (a parse or type error naming line and column, a bad
  `${...}`, a binding error above) is `error`, with the last line of its message as
  detail (`execution_error`); the traceback goes to stderr. A legacy request is
  `unsupported` ("Legacy submissions are not supported by idp_z3").
- The engine's diagnostics go to stderr; only the protocol records go to stdout.

## Compilation

None: parsing, grounding and solving all happen inside the execution budget.
`compilation_timeout` does not apply.

## Environment

Image `dcp-eval/idp_z3:v1` (`python:3.12.11-slim-bookworm`): Python 3.12.11 at
`/usr/local/bin/python`, idp-engine 0.12.1 with the z3-solver 4.11.2.0 it pins, sli-lib
0.4.6, textX 2.3.0, Arpeggio 2.0.3, RestrictedPython 8.5, python-dateutil, six (verified
with `pip list` in the image). The model is FO(.) only and imports nothing; the runner
uses the standard `json`. No edition or size limits, no environment variables set for the
solver.

The evaluator runs the container with no network, a read-only root file system, user
65534, `HOME=/tmp`, the working directory `/tmp` (a 512 MiB tmpfs), `/input` read-only
holding only `model.idp` and `request.json`, 1 CPU and 2048 MiB (verified with the
evaluator's flags: `uid=65534(nobody)`, `/` read-only, `/tmp` 512M tmpfs). The image's
entrypoint is the runner (`python /opt/runner/run.py`); for an ad hoc run override it:
`docker run --rm --network none --entrypoint sh dcp-eval/idp_z3:v1 -c 'python -c "..."'`.

## Traps

- **Two reasons for "refused" data.** Rule-5 shapes, declared strings and floats, and
  name clashes are `unsupported_capability`, not `execution_error`; type sizing conflicts,
  arity mismatches and bad `${...}` are `execution_error`.
- **Your own `structure` interpreting a data symbol** stops the runner from binding it:
  the instance value is silently ignored, which is hardcoding the evaluator rejects on the
  next instance.
- **A declared data symbol that no instance field or piece provides** (a misspelled
  field, or `F_1` of a field whose shape is refused) is not an error: it is simply left
  uninterpreted, a free unknown z3 may choose. Name data symbols exactly as the brief
  lists the fields.
- **`type T` without `<: Int`** is never sized from data and is not numeric.
- **A 0/1 integer field declared `-> Bool`** binds as all false (only JSON `true` counts),
  without an error naming the field; the evaluator then reports a wrong solution.
- **Arrays bind 0-based**: an instance holding 1-based coordinates or ids must be shifted
  in the constraint (`r + 1 = lt(k, 0)`), and ragged padding is 0, so compare 1-based ids
  or guard with `F_len`.
- **`${...}` is substituted everywhere**, comments included: a malformed placeholder in a
  comment still fails the run.
- **The structure name `_dcp_instance`** is the runner's; do not declare it.

## Example

The pilot fixture [tests/fixtures/model_idp.idp](../../tests/fixtures/model_idp.idp)
(instance fields `n`, `optimize`; outputs `x`, `y`):

```
vocabulary {
    type V := {0..${n}}
    n: () -> Int
    optimize: () -> Bool
    x: () -> V
    y: () -> V
    minimize: () -> Int
}
theory {
    optimize() => x() + y() >= n().
    ~optimize() => x() + y() = n().
    minimize() = x() + y().
}
```
