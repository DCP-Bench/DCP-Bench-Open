# swipl_clpfd: how this integration realises the submission contract

Read [the submission contract](../CONTRACT.md) first; this file only says how SWI-Prolog
CLP(FD) expresses it. Runner: [run.py](run.py), which starts the driver
[driver.pl](driver.pl) in a separate `swipl` process and relays what it prints. The
driver consults the submission, calls `model/3` or `model/4`, owns labelling,
optimisation and enumeration, and prints the protocol records on stdout.

## Submission file

One Prolog file, `model.pl`, consulted into the same `user` module as the driver. It
loads what it uses itself (`:- use_module(library(clpfd)).`); the SWI-Prolog standard
library is available, no other file of yours is staged.

## Entrypoint

```prolog
model(+Instance, -Vars, -Outputs)              % satisfaction
model(+Instance, -Vars, -Outputs, -Objective)  % optimisation (preferred if both exist)
labeling_options(-Options)                     % optional, default [ff]
```

The driver calls the model once to prove the optimum (when `model/4` exists) and once
more to enumerate. `Vars` is the finite-domain variables to label; the driver labels
`term_variables(Vars-Outputs)`, so nesting is fine and output variables are always
labelled. `labeling_options/1`, if defined, must give a list of clpfd `labeling/2`
options without `min/1` or `max/1`. A `model/3`/`model/4` that fails is reported as
`unsat`.

## Instance

`Instance` is the instance JSON as a **dict** (`json_read_dict` with
`value_string_as(atom)`): read a field with `Instance.n` or `get_dict(n, Instance, N)`;
a capitalised name needs quotes, `get_dict('N', Instance, N)`. Values:

- integers and floats as numbers;
- JSON `true` / `false` / `null` as the **atoms** `true` / `false` / `null` (test with
  `== true`);
- **strings as atoms** (`atom_chars/2` or `atom_codes/2` take one apart);
- arrays as Prolog lists, ragged allowed, with no inherent index base: use `nth1/3` or
  `nth0/3` consistently, and remember `element/3` is 1-based;
- nested objects as dicts.

## Outputs

`Outputs` is a **nonempty list of `Name-Value` pairs**, one per declared output, with
`Name` an atom (`'A'-Xs` for a capital). `Value` is an integer, a variable, or a nested
list of these to the declared shape; it must be ground after labelling, or the run is an
`error`. The driver writes the pairs with `json_write_dict`: integers as numbers, lists
as arrays, the atoms `true`/`false` as JSON Booleans, any other atom as a JSON string
(which the evaluator rejects). A repeated name is an `error`. Solutions whose output
object repeats one already printed are dropped.

## Objective

The fourth argument of `model/4` is `min(Expr)`, `max(Expr)` or `none`, with `Expr` a
clpfd arithmetic expression. The driver runs `once(labeling([min(Expr)|Options], Vars))`
(or `max`), takes the first solution as the optimum, then calls the model again, posts
`Expr #= Optimum` and enumerates with `labeling(Options, Vars)`. Anything else in that
position is an `error`.

## Compilation

No separate step. The file is consulted at run time, inside the execution budget
(`execution_timeout`, enforced by `call_with_time_limit` around each phase, with a 4 s
backstop kill in `run.py`); `compilation_timeout` does not apply. The process runs with
`--stack-limit=1g`.

## Environment

Image `dcp-eval/swipl_clpfd:v1`: the official `swipl:9.2.9` image, with
`library(clpfd)`; the runner around it is Python 3 from that image.

## Traps

- **Put every auxiliary variable in `Vars`.** Only `Vars` and output variables are
  labelled; a constraint on an unlabelled auxiliary only has to stay consistent, so a
  reported solution can violate it (`invalid_solution`). The same goes for variables
  that appear only in the objective `Expr`: an unlabelled one leaves the optimum
  non-ground and the run errors.
- **Never print.** stdout is the protocol: any non-JSON line (from `format/2`, `write/1`,
  a directive at load time) makes the run an `error`.
- **`labeling_options/1` must not hold `min/1`/`max/1`** and must be a list; the
  objective belongs to `model/4`.
- **Keep the model deterministic**: enumeration backtracks through `labeling/2` and then
  into `model/3,4`; leftover choice points would build and report a different model.
- The driver's own predicates live in the same module (`run/0`, `solve/5`, `build/4`,
  `search/5`, `optimum/3`, `enumerate/6`, `record/1`, `status/2`, `report/1`, ...). Do
  not define predicates with those names and arities.
- A syntax error does not stop the consult: the clause is skipped with a message on
  stderr, which typically surfaces as "defines neither model/3 nor model/4" or `unsat`.
- The old skill says `true`/`false` outputs arrive as JSON strings; `json_write_dict`
  writes those atoms as JSON Booleans, which are accepted. `0`/`1` works as well.

## Example

The pilot fixture [tests/fixtures/model_swipl.pl](../../tests/fixtures/model_swipl.pl)
(instance fields `n`, `optimize` (arriving as the atom `true`/`false`); outputs `x`, `y`):

```prolog
:- use_module(library(clpfd)).

model(Instance, [X, Y], [x-X, y-Y], Objective) :-
    N = Instance.n,
    [X, Y] ins 0..N,
    (   Instance.optimize == true
    ->  X + Y #>= N,
        Objective = min(X + Y)
    ;   X + Y #= N,
        Objective = none
    ).
```
