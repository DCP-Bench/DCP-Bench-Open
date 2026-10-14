# DCP-Bench Open: how instances become parameters

Source: `solvers/essence_prime_minion/run.py`. The model declares each instance field it reads with `given`; only
declared givens are bound, as one `letting NAME = VALUE` each. An instance field no `given` names is ignored,
whatever its type, so `name` and `note` need no declaration. Names in `given` lines may be comma-separated lists;
`$` comments are ignored. A declared given with no value is `execution_error`.

1. int, bool, rectangular list of them: binds unchanged.
2. Ragged list of rows whose items have one shape and whose scalars have one type: binds as `<field>` padded with
   0 (false for bools) to the longest row, plus `<field>_len`.
3. Equal-length rows with columns of different types: `<field>_1`, `<field>_2`, ...; `<field>` is not bound. Each
   column then follows rule 1 or 2 (not split again).
4. Derived sizes, bound only when declared: `<field>_len` (length of each row, for a list of lists) and
   `<field>_dim1`, `<field>_dim2`, ... (length along each axis of every bound list, after padding). Use them for
   sizes that vary per instance:
   ```
   given grid_dim1, grid_dim2 : int
   given grid : matrix indexed by [int(1..grid_dim1), int(1..grid_dim2)] of int
   ```
   Essence' needs finite index domains, so a size that varies must come from a given like this. Lists nested three deep bind padded the same way, with `<field>_dim1` to `<field>_dim3` and `<field>_len` when declared. A size that is not a field but equals a list's length is declared as `given grid_dim1 : int` and `letting n = grid_dim1` (run).
5. Refused with `execution_error` naming the field: a declared field that is a float, string or empty list, a name that
   is not an identifier, other ragged or mixed shapes, and generated names that collide with an instance field.

`generation.brief` lists `unbindable_fields` with a generic rule (ragged or mixed rows), which is looser than this
binding. `generation.next_work` withholds a problem for this integration only when `run.py`'s `refusal` rejects a field
in some instance, that is, when no model could bind it (rule 5 shapes). A string field does not withhold a problem: a
model that does not declare it runs, and a model that declares it is refused for that run.

Parameter order does not matter: Savile Row resolves lettings in any order, so dims may come after the matrix.

Essence' reserved words cannot be names. A field or output named `matrix`, `int`, `where` and the like is written
`matrix_` in the model (`given where_ : int`, `find matrix_ : int`); the solution value is reported as `matrix`.
The list is in `run.py` (`RESERVED`).

## Solving

- Output variables: every `find`; the declared outputs are read by name and compared with the reference's
  solution set. Other `find`s are not compared: solutions are projected onto the declared outputs.
- Auxiliary `find`s (not fixed by the outputs): pin each to a function of the outputs, or leave it out. A free
  auxiliary multiplies the solutions the enumeration must rule out.
- Shapes: `generation.brief` takes output shapes from the reference example's values. Size each output matrix
  from an instance `given` (see the sizes example in item 4 above), not from the example's numbers.
- Satisfaction: each round asks Savile Row for the solutions still missing, then adds a nogood per output
  assignment found (`!(x = 1 /\ M[1,2] = 3 ...)`, matrices flattened), so each round gives new output
  assignments or shows that none remain. Stops at the limit, at exhaustion, or at timeout.
- Optimisation: run 1 solves the model; its result is used only when Minion finished. Run 2 replaces the
  objective line by `find dcp_objective_value : int(-10^12..10^12)` plus `minimising/maximising dcp_objective_value`
  and the constraint `dcp_objective_value = EXPR`, reads the optimum, then run 3 drops the objective and adds
  `EXPR = optimum` for enumeration, with the same nogood rounds. Needs exactly one objective, alone on its line.
- `such that` is a single block: the runner appends `,\nCONSTRAINT` after the model's last constraint, or adds a
  `such that` line when there is none. A second `such that` in the model breaks this.
- Budget: Savile Row's `-timelimit` and Minion's `-cpulimit` come from the evaluation's execution timeout.

## Evaluator reasons

`execution_error` Savile Row failed (message in stderr, parse errors name a line) or a declared given could not be
bound (named in `detail`); `invalid_output` names or value types wrong; `invalid_solution` a solution the reference
rejects; `no_solution` the model is unsatisfiable; `suboptimal_solution` wrong direction or objective;
`execution_timeout` no proof or no finish in time.
