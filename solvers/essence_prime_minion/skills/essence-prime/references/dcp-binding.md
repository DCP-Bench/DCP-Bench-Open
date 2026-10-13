# DCP-Bench Open: how instances become parameters

Source: `solvers/essence_prime_minion/run.py`. The JSON instance becomes one parameter file, one
`letting NAME = VALUE` per bound field; the model declares each used field with `given`.

1. int, bool, rectangular list of them: binds unchanged. A nonempty list of lists also binds
   `<field>_len` (the length of each row) unless an instance field already has that name.
2. Ragged list of rows whose items have one shape and whose scalars have one type: binds as
   `<field>` padded with 0 (false for bools) to the longest row, plus `<field>_len`.
3. Equal-length rows with columns of different types: `<field>_1`, `<field>_2`, ...; `<field>` is
   not bound. Each column then follows rule 1 or 2 (not split again).
4. Refused with `execution_error` and a message naming the field: floats, strings, empty lists, field
   names that are not identifiers (or are reserved words), other ragged or mixed shapes, and generated
   names that collide with an instance field.

Declare matrix `given`s with fixed index domains, e.g. `matrix indexed by [int(1..n), int(1..maxlen)] of int(0..)`;
pad-length and row count come from other fields (`n`, or a field you compute with `letting maxlen = max(rows_len)`).
Padding values are 0/false, so use `_len` to ignore them.

## Solving

- Output variables: every `find`; the declared outputs are read by name and compared with the
  reference's solution set. Outputs not found in the solution fall back to all variables (then
  `invalid_output`).
- Satisfaction: `-num-solutions N`, asking again with 4x more when duplicates on the outputs left too
  few, until the limit or Minion finishes (`SolverTimeOut:0`).
- Optimisation: run 1 solves the model; its result is used only when Minion finished. Run 2 replaces the
  objective line by `find dcp_objective_value : int(-10^12..10^12)` plus `minimising/maximising dcp_objective_value`
  and the constraint `dcp_objective_value = EXPR`, reads the optimum, then run 3 drops the objective and adds
  `EXPR = optimum` for enumeration. Needs exactly one objective, alone on its line.
- `such that` is a single block: the runner appends `,\nCONSTRAINT` after the model's last constraint, or adds a
  `such that` line when there is none. A second `such that` in the model breaks this.
- Budget: Savile Row's `-timelimit` and Minion's `-cpulimit` come from the evaluation's execution timeout.

## Evaluator reasons

`execution_error` Savile Row failed (message in stderr, parse errors name a line); `invalid_output` names or
value types wrong; `invalid_solution` a solution the reference rejects; `no_solution` the model is unsatisfiable;
`suboptimal_solution` wrong direction or objective; `execution_timeout` no proof or no finish in time.
