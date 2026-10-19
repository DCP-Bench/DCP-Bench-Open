# essence_prime_minion: how this integration realises the submission contract

Read [the submission contract](../CONTRACT.md) first; this file only says how Essence'
through Savile Row 1.11.1 and Minion expresses it. Runner: [run.py](run.py), which builds an
Essence' parameter file from the instance, runs Savile Row with Minion, and plugs its own
`essence_solver` into `main("essence")` of [runner/runtime.py](../../runner/runtime.py)
(request parsing, the overall timer and error handling stay runtime's).
[metadata.yaml](metadata.yaml) declares `instance_binding: reshaped`: the runner's own
`refusal()` decides which instance fields no model can bind (see [Instance](#instance)).

## Submission file

One Essence' file, `model.eprime`, starting with `language ESSENCE' 1.0`. No parameter
file: the runner writes it from the instance. No other file of yours is staged, and the
model cannot read files.

## Entrypoint

There is no function: the runner hands the whole file to Savile Row together with a
generated `model.param`, and reads from the model:

- the `given` lines, to know which instance fields to bind (see [Instance](#instance));
- the `find` variables, whose solution values it reads back by name (see [Outputs](#outputs));
- an optional `minimising EXPR` / `maximising EXPR` line (see [Objective](#objective));
- the single `such that` list, to which it appends constraints (see [Solving](#solving)).

## Instance

The instance becomes an Essence' parameter file: `language ESSENCE' 1.0` followed by one
`letting NAME = VALUE` per bound name. Booleans are `true`/`false`; lists become matrix
literals, which Savile Row indexes from **1** (the instance's index 0 is `F[1]`).
Savile Row resolves lettings in any order, so a size given may come after the matrix it
sizes.

**Only declared givens are bound.** The runner collects the names on every `given NAME :`
line (comma-separated lists such as `given a, b : int` included; `$` comments are ignored)
and binds those names and nothing else. An instance field that no `given` names is
ignored, whatever its type, so `name`, `note` and other string fields never reach Savile
Row. A declared given with no value (no such instance field, and no field it is a derived
size of) is refused: ``Declared given `absent` has no value: the instance has no such
field, and no field it is a size of``. A given's domain must hold every instance value
(`0` is not in `int(1..)`).

Essence' has no strings or floats and a matrix literal must be rectangular, so a declared
field is bound by these rules:

1. **An int, a Boolean, or a rectangular list of them** (one scalar type) binds unchanged.
   When it is a nonempty list of lists, `<field>_len` (each row's length) is also
   available.
2. **A ragged list of rows whose items all have one shape and whose scalars have one
   type** binds as `<field>` padded to the longest row with `0` (or `false` for Booleans),
   plus `<field>_len`. Rows of equal-shape arrays gain one dimension (padded with a block
   of zeros of that shape). `<field>_dim1` is then the number of rows and `<field>_dim2`
   the padded longest row. Padding can equal a real value: read row `i` only up to
   `<field>_len[i]`.
3. **Equal-length rows whose columns have different types** (Booleans beside integers,
   scalars beside arrays) bind as one matrix per column, `<field>_1`, `<field>_2`, ...,
   numbered from 1; `<field>` itself is **not** bound. Each column then binds by rule 1
   or 2, but is not split again. Rows `[target, cells]` with `cells` ragged give `F_1`
   (the int column) and `F_2` (padded, 3-D, with `F_2_dim1` to `F_2_dim3` and `F_2_len`);
   index a padded cell by `k <= F_2_len[c]`.
4. **Derived sizes**: `<field>_dimK` (K from 1) is the length along axis K of every list
   bound by rules 1 to 3, after padding (lists nested three deep get `_dim1` to `_dim3`).
   `<field>_len` and `<field>_dimK` are bound **only when a given declares them**, and an
   instance field of the same name wins over a derived one.
5. **Refused**, as status `error` naming the field (reason `execution_error`), only when
   the model declares it: a float, a string (`` Instance field `name` holds a string
   value; Essence' parameters are integers, Booleans and matrices of them ``), an empty
   list or one nested anywhere inside the field (`` ... contains an empty list, which an
   Essence' matrix literal cannot express ``; its `_dimK` sizes still bind when only they
   are declared), a name that is not an Essence' identifier, a ragged or
   mixed field outside rules 2 and 3 (`` Instance field `rows` is ragged or mixes types
   in a way this integration cannot bind ... ``), and a generated name (`<field>_1`, ...)
   that collides with an instance field or another generated name.

Essence' needs finite index domains, so every size that varies per instance must come from
a given. Declare the sizes beside the field:

```
given grid_dim1, grid_dim2 : int
given grid : matrix indexed by [int(1..grid_dim1), int(1..grid_dim2)] of int
```

This holds for a plain list too (`given F_dim1 : int` and `given F : matrix indexed by
[int(1..F_dim1)] of int`). A size that is not an instance field but equals a list's length
is declared as its `_dim` given and renamed: `given grid_dim1 : int` then `letting n =
grid_dim1`. A matrix given sized with the example's numbers fails on another instance with
Savile Row's `Index domains do not match for the matrix F`.

**Reserved words.** A field or output whose name is an Essence' or Savile Row word is
written with a trailing `_` in the model (`given where_ : int`, `find matrix_ : int`): it
binds under that name, and a solution value `matrix_` is reported as `matrix`. The words
(`RESERVED` in run.py): `forall forAll exists sum such that letting given where find
language int bool union intersect in false true matrix indexed by of be domain minimising
maximising branching on heuristic toInt flatten table alldiff allDiff`.

**Which problems are withheld.** `generation.brief` lists `unbindable_fields` by a generic
rule (any ragged or mixed field), which is looser than this binding. For this integration
`generation.next_work` withholds a problem only when run.py's `refusal(name, value)`
rejects a field (other than `name` and `note`) in some instance, that is, a rule-5 shape
no model could bind. `refusal` checks only the shape: a string, float or empty-list field
does not withhold a problem, since a model that does not declare it runs, and a model that
declares it is refused for that run.

## Outputs

Each declared output is a `find` variable named exactly as the output (escaped with `_`
if reserved), with the declared shape: an `int(lo..hi)` or `bool` scalar, or a nested
`matrix indexed by [...]`. The runner reads every `find` back from Savile Row's solution
files (`letting NAME be VALUE`), parses ints, `true`/`false` and nested matrix literals
(skipping any index-domain annotation, so a matrix becomes a plain JSON list by
position), and projects each solution onto the declared outputs. Booleans are reported as
JSON Booleans. A matrix is reported by position, so its first element (`M[1]` for a
matrix indexed from 1) is the reference's index 0. Other `find` variables are auxiliary
and never reported. If a declared
output is missing from the solution, the runner does not project and reports every `find`
variable, which the evaluator rejects as `invalid_output`.

An output that is a function of other variables is a `find` of its own, constrained with an
equality, so the runner reads its value. The evaluator matches output values to the
reference's exactly, so each output is pinned by constraints and not left a range. Leaf kind
follows the brief: an output the brief shows as `int` is an `int(...)` `find`, even where the
statement speaks of yes or no; a `bool` leaf is reported as a JSON Boolean and is rejected
where an integer is expected.

## Objective

One line, alone, `minimising EXPR` or `maximising EXPR`, with an integer expression, after
any `branching on`/`heuristic` and before `such that`. No objective for a satisfaction
problem. Any whole-word `minimising`/`maximising` outside `$` comments makes the run an
optimisation.

To enumerate more than one solution, the runner needs the objective to match
`^[ \t]*(minimising|maximising)[ \t]+(\S[^\n]*?)[ \t]*$` (multiline) **exactly once**,
both in the comment-free source and in the raw source; otherwise a run asked for more
than one solution ends as `unsupported` ("Enumeration requires `minimising EXPR` or
`maximising EXPR` on its own line"), which the evaluator reports as
`unsupported_capability`. The runner restates `EXPR` in parentheses itself (`(EXPR) =
v`), so an unparenthesised `minimising sum i : D . c[i]` is fine.

## Solving

Each call is one Savile Row run that also runs Minion, from a fresh directory under
`/tmp`:

```
java -XX:ParallelGCThreads=1 -XX:+UseSerialGC -Xmx1200m -Djava.library.path=/opt/savilerow/lib
  -jar /opt/savilerow/savilerow.jar model.eprime model.param -run-solver
  -minion-bin /opt/savilerow/bin/minion -timelimit S -solver-options "-cpulimit S"
  -out-solution out.solution -out-info out.info -out-minion out.minion -out-aux out.aux
  [-num-solutions K]
```

The submission cannot change these flags (its own `branching on` and `heuristic` still
apply). Savile Row's stdout and stderr go to the run's stderr.
No `-S` flag is passed, so Savile Row's default `-S1` applies: it may fix a `find` it
considers unused (see [Traps](#traps)).

- **Status of one call**: `SavileRowTimeOut:1` in the info file, or the process outliving
  its wait, is `timeout`; a nonzero exit is `error` with detail `Savile Row exited N; see
  stderr` (the Savile Row message, e.g. a parse error naming the line, is in `stderr`);
  `SolverTimeOut:0` means Minion finished its search.
- **Optimisation**: run 1 solves the model as written; its single solution is used only
  when Minion finished (`SolverTimeOut:0`). Minion's info file has no separate optimality
  key, so an unfinished search is `timeout` ("Candidate optimum was not proven") with no
  solution reported, never the incumbent. No solution after a finished search is `unsat`.
  With a solution limit of 1 the run stops there (`limit`). Otherwise run 2 replaces the
  objective line by `find dcp_objective_value : int(-1000000000000..1000000000000)` and
  `minimising/maximising dcp_objective_value`, adds `dcp_objective_value = (EXPR)`, and
  reads the optimum back; run 3 onwards drop the objective line, add `(EXPR) = optimum`,
  and enumerate as for satisfaction.
- **Enumeration** (satisfaction, or pinned at the optimum): each round asks Savile Row
  for the solutions still missing (`-num-solutions want`). Savile Row enumerates every
  `find`, so a free auxiliary variable repeats an output assignment: the runner keeps a
  solution only if its projection onto the declared outputs is new (compared as sorted
  JSON). After each round it adds one nogood per output assignment found,
  `!(x = 1 /\ M[1, 2] = 3 /\ ...)`, matrices flattened to elements by **1-based position**,
  and runs again from scratch. It stops with `limit` once enough distinct assignments are
  out; with `timeout` if Minion did not finish; and with `complete` (or `unsat` if nothing
  was found) when a finished round returned fewer solutions than asked.
- **Adding constraints**: the runner appends `,\n<constraint>` to the end of the file when
  the comment-free model contains `such that`, else `\nsuch that\n<constraint>`.
- **Time**: the deadline is `execution_timeout` from the start of `essence_solver`. Each
  call gets `S = int(seconds left) - 2` (at least 1) as both `-timelimit` and Minion's
  `-cpulimit`, and is killed (with its process group) when the time left runs out; with
  2 s or less left, the call is not started and the run is `timeout`. A `SIGALRM` at
  exactly `execution_timeout` from the start of `main` also turns into `timeout`; on that
  path, solutions already found are not emitted.
- Any exception (a refused binding, an unreadable solution file) is `error` with the
  message as detail, i.e. `execution_error`.

## Compilation

No separate step: Savile Row translates the model to Minion inside each run, within the
execution budget (`-timelimit`). `compilation_timeout` does not apply.

## Environment

Image `dcp-eval/essence_prime_minion:v1`, from
`eclipse-temurin:17-jre-jammy` (Ubuntu 22.04, Java 17 JRE): Savile Row 1.11.1 (release
tarball, checksum-pinned) unpacked in `/opt/savilerow` with its bundled Minion at
`/opt/savilerow/bin/minion` (`fzn-chuffed` and `kissat` removed), and Ubuntu's `python3`
for the runner at `/opt/runner/run.py`. The `savilerow` launcher script is
`/opt/savilerow/savilerow`, and `/opt/savilerow` is not on the image's `PATH` (it is
`/opt/java/openjdk/bin` and the system directories), so a bare `savilerow` is `not found`
inside the image; the runner calls the jar directly. An ad hoc run gives the launcher's full
path or prepends `/opt/savilerow` to `PATH`. The model can use only Essence' itself; no JSON
or other library is involved on the model's side. The JVM heap is capped at 1200 MB
inside the evaluator's 2048 MiB container limit, so a quantifier over a very large domain
exhausts Savile Row's memory (`memory_limit` or a Java error).

The evaluator runs the container with no network, a read-only root file system, user
65534, `HOME=/tmp`, the working directory `/tmp` (a 512 MiB tmpfs), `/input` read-only
holding only `model.eprime` and `request.json`, 1 CPU and 2048 MiB. The image's
entrypoint is the runner (`python /opt/runner/run.py`); for an ad hoc run override it:
`docker run --rm --network none --entrypoint sh dcp-eval/essence_prime_minion:v1 -c
'cd /tmp && java -jar /opt/savilerow/savilerow.jar ...'`.

## Traps

- **`such that` once, and last.** The runner appends `,\n<constraint>` to the end of the
  file. A second `such that`, an empty `such that`, a trailing comma, or a `$` comment
  after the last constraint (the comma lands inside the comment) breaks every enumeration
  or optimisation round with a Savile Row parse error.
- **Objective alone on its line.** A second objective line, or an objective split over
  lines, gives `unsupported_capability` whenever more than one solution is asked.
- **Index output matrices from 1** (`matrix indexed by [int(1..n)]`). Nogoods address
  elements by 1-based position; a matrix indexed from 0 gets nogoods on the wrong
  elements (out-of-range ones are false, so nothing is excluded), and enumeration repeats
  or misses solutions.
- **Free auxiliary `find`s** do not create false duplicates (solutions are projected and
  deduplicated), but each repeat costs a Savile Row round. Pin each auxiliary `find` to a
  function of the outputs, or leave it out.
- **Sizes from givens, not from the example.** A matrix given or output whose index
  domain uses the example's numbers fails on another instance (`Index domains do not
  match for the matrix F`). Use `F_dimK` givens.
- **A given whose name starts with `<field>_`** makes the runner reshape `<field>` to look
  for derived names, so an unbindable `<field>` is then refused even though `<field>`
  itself is not declared. Avoid given names that begin with another field's name and `_`
  unless they are its derived sizes.
- **`dcp_objective_value`** is the runner's own name; do not use it. An objective outside
  `-10^12..10^12` cannot be read back.
- **An output fixed by `-S1`.** Savile Row's default `-S1` fixes a `find` whose only
  constraints are unary (they fold into its domain) or that no constraint mentions. The
  first enumeration round then returns one solution where several exist, fewer than asked,
  and the runner reports `complete`: e.g. `find x : int(1..3)` with only `x != 2` and a
  solution limit of 5 reports only `x = 1`. Constrain such an output in a way that is not
  unary, or accept that only one value is enumerated.
- **`min` and `max` are reserved but not escaped.** Savile Row rejects them as names
  (`ERROR: Parsed keyword 'max'`), and they are not in `RESERVED`, so `given max_` is not
  bound to a field `max` (``Declared given `max_` has no value``) and an output named
  `min` or `max` cannot be declared at all.
- **Rule-3 fields have no `<field>`**: declaring `given F` for a mixed-row field is a
  missing given; declare `F_1`, `F_2`, ....

## Example

The pilot fixture [tests/fixtures/model_essence.eprime](../../tests/fixtures/model_essence.eprime)
(instance fields `n`, `optimize`; outputs `x`, `y`):

```
language ESSENCE' 1.0
given n : int(0..100)
given optimize : bool
find x : int(0..n)
find y : int(0..n)
minimising optimize * (x + y)
such that
    (optimize -> x + y >= n) /\ (!optimize -> x + y = n)
```
