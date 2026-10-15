# minizinc_gecode: how this integration realises the submission contract

Read [the submission contract](../CONTRACT.md) first; this file only says how MiniZinc on
Gecode expresses it. Runner: [run.py](run.py), which reshapes the instance and then calls
`minizinc_solver` in [runner/runtime.py](../../runner/runtime.py) through `main("minizinc")`.

## Submission file

One MiniZinc file, `model.mzn`. It may use the MiniZinc standard library (`include
"globals.mzn";` and the like); no other file of yours is staged, so it cannot `include`
one.

## Entrypoint

There is no function: the runner loads the whole file as a MiniZinc model, binds the
instance as data, and reads three items from it:

- one parameter declaration per instance field it uses, with no value assigned
  (`int: n;`, `array[int] of int: demand;`);
- one solve item: `solve satisfy;`, or `solve minimize objective;` /
  `solve maximize objective;` (see [Objective](#objective));
- one `output` item (see [Outputs](#outputs)).

## Instance

Every JSON field is assigned as MiniZinc data under its own name, through the MiniZinc
data interface (minizinc-python `inst[key] = value`). A field the model does not declare
is ignored; a declared parameter the instance lacks is a MiniZinc error. Integers bind to
`int`, Booleans to `bool`, strings to `string`, floats to `float`. Every array is indexed
from **1**: declare `array[int] of ...`, `array[int,int] of ...` (or use
`index_set`/`index_set_1of2`), never `0..n-1`. Fields MiniZinc cannot take as they are
are reshaped by `run.py`:

1. **Accepted as is** (a scalar, or a rectangular array of one scalar type): bound
   unchanged. If it is a nonempty list of lists, `<field>_len` (each row's length,
   `array[int] of int`) is also bound, unless an instance field already has that name.
2. **Ragged list of rows** whose items share one shape and one scalar type: `<field>` is
   bound padded to the longest row with `0`, `false`, `0.0` or `""`, plus `<field>_len`.
   Rows of equal-shape arrays gain one dimension (`[[[0,3],[1,2]],[[1,4]]]` binds as
   `array[int,int,int]`, padded with `[0,0]`). Padding can equal a real value, so read
   row `i` only up to `<field>_len[i]`.
3. **Equal-length rows whose columns differ in type** (strings beside numbers, scalars
   beside arrays): one array per column, `<field>_1`, `<field>_2`, ..., numbered from 1;
   `<field>` itself is **not** bound. Each column then binds by rule 1 or 2 (not split
   again). `[["Epic",1,30],["Chain 1",1,6]]` gives `movies_1` (strings), `movies_2`,
   `movies_3` (ints).
4. Anything else ragged or mixed, or a generated name that clashes with an instance field
   or another generated name, is refused: status `error` naming the field, before the
   model runs.

Declare `<field>_len` whenever a field is ragged in any instance of the problem: rule 1
binds it for an instance whose rows happen to be equal, so the same model runs on both.
Iterate a padded field row by row up to its length, never over the padded width:

```minizinc
array[int,int] of int: rules;
array[int] of int: rules_len;
constraint forall(i in index_set_1of2(rules), j in 1..rules_len[i])(x[rules[i,j]] > 0);
```

## Outputs

The `output` item must print **exactly one JSON object**, keyed by the declared output
names. The runner parses the printed text with a strict JSON parser (duplicate keys and
non-finite numbers are rejected), so any other text in the output item fails the run.
`show(x)` of an `int` or `bool` prints valid JSON (`3`, `true`); for a one-dimensional
array `show` prints `[1, 2, 3]`. For arrays of two or more dimensions use
`showJSON(g)`, which nests (`[[1, 1, 0], [0, 0, 0]]`); `show(g)` flattens it.
Auxiliary variables simply stay out of the output item.

## Objective

Declare an integer variable named exactly `objective`, tie it to the objective
expression, and write the solve item **alone on its own line, unannotated**:

```minizinc
var int: objective = sum(i in 1..n)(cost[i] * x[i]);
solve minimize objective;
```

The runner first solves with Gecode and accepts only `OPTIMAL_SOLUTION`. To enumerate
more than one solution it then finds the solve item with the regex
`^\s*solve\s+(minimize|maximize)\s+objective\s*;\s*$` (multiline), which must match
exactly once, replaces it with `constraint objective = <optimum>;` and `solve satisfy;`,
and enumerates all solutions of that model. A solve item that does not match (an
annotation, a trailing comment, an expression instead of `objective`, a second matching
line) gets status `unsupported` whenever more than one solution is requested.

## Solving

- The runner passes no solver flags: Gecode runs with MiniZinc's defaults (one thread,
  the model's own search, or Gecode's default search when there is none).
- Optimisation is one `solve` call with `intermediate_solutions=False`: `OPTIMAL_SOLUTION`
  is the first solution, `UNSATISFIABLE` is `unsat`, and any other status (a solution not
  proven optimal, `UNKNOWN`) is `timeout`.
- Enumeration (satisfaction, or the rewritten model pinned at the optimum) streams every
  solution of the whole model with `all_solutions=True`; nothing is added to the model,
  and a solution whose printed output object repeats one already reported is dropped.
  It stops at `limit` once enough distinct objects are out; MiniZinc's `ALL_SOLUTIONS` or
  `UNSATISFIABLE` is exhaustion (`complete`, or `unsat` with nothing reported); a stream
  that ends any other way is `timeout`.
- The time budget is `execution_timeout` from the start of the run: each MiniZinc call
  gets what is left as its `time_limit`, and a timer around the whole run turns an
  overrun into `timeout`.

## Compilation

No separate step: MiniZinc flattens the model to FlatZinc inside the execution budget
(the runner's `execution_timeout`, enforced with a timer around the whole run).
`compilation_timeout` does not apply.

## Environment

Image `dcp-eval/minizinc_gecode:v1`: MiniZinc 2.9.3 (from the `minizinc/minizinc:2.9.3`
image) with its bundled Gecode 6.3.0, driven from Python 3.12.11 by minizinc-python
0.10.0. The model can use only the MiniZinc standard library (`/usr/local/share/minizinc/std`);
it needs no JSON library, since `showJSON` and string concatenation build the output.
`minizinc` is on `PATH` at `/usr/local/bin/minizinc`; no environment variables are set
for it. The evaluator runs the container with no network, a read-only root file system,
user 65534, `HOME=/tmp`, a 512 MiB writable `/tmp` and `/input` read-only. For an ad hoc
run, override the entrypoint: `docker run --rm --network none --entrypoint sh
dcp-eval/minizinc_gecode:v1 -c 'minizinc --solver gecode ...'`.

## Traps

- **Search annotations break enumeration.** `solve :: int_search(...) minimize
  objective;` solves once but cannot be rewritten, so a multi-solution run is
  `unsupported`. Keep the solve item bare.
- **`show` on a 2-D array flattens it**, giving an `invalid_output` shape. Use `showJSON`.
- **Some ragged or mixed fields are unbindable** (rule 4); no model can work around that,
  so the problem/integration pair is blocked. `python -m generation.brief` lists them
  under `unbindable_fields`.
- **Do not declare `<field>` for a rule-3 field**: only `<field>_1..._k` exist, so a
  declared `<field>` is an undefined parameter.
- Enumeration solves all solutions of the whole model and drops repeats of an output
  object already reported, so free auxiliary variables make enumeration slower, not
  wrong.

## Example

The pilot fixture [tests/fixtures/model.mzn](../../tests/fixtures/model.mzn) (instance
fields `n`, `optimize`; outputs `x`, `y`):

```minizinc
int: n;
bool: optimize;
var 0..n: x;
var 0..n: y;
constraint if optimize then x+y >= n else x+y = n endif;
var int: objective = if optimize then x+y else 0 endif;
solve minimize objective;
output ["{\"x\":", show(x), ",\"y\":", show(y), "}"];
```
