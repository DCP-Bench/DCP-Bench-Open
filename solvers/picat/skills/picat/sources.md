# Sources for `picat`

Documentation this skill's instructions were written from. Add an entry whenever
a claim here comes from a specific page or version.

- <https://picat-lang.org/download.html> — Picat 3.9#12, released 2026-08-28, the build this integration installs, accessed 2026-09-29
- `Picat/doc/constraints.tex` in `picat39_12_linux64.tar.gz` — the Constraints chapter of the Picat guide: domain variables, table, arithmetic, Boolean and global constraints, and the solving options of the cp and sat modules
- `Picat/doc/module.tex` in the same archive — static binding of calls, and the run-time search that call/N performs over the loaded modules
- `Picat/doc/all.tex` in the same archive — maps (`get/2`, `put/3`), `vars/1`, `read_term/1`, `findall/2`, loops and `if` statements
- `Picat/LICENSE` in the same archive — Picat is free for any purpose; its C sources are under the Mozilla Public License 2.0

Every constraint in the table and every trap in this skill was checked by
running a submission through the `dcp-eval/picat:v1` image, with `import cp.`
and again with `import sat.`, and comparing the solutions with a brute-force
enumeration where the count was not obvious:

- Instance data: `Data.get(key)` on lowercase, capitalised (`'NUM_CELLS'`) and
  underscore (`'_SHIP'`) keys; lists of lists indexed as `Grid[2, 1]`; strings;
  a JSON Boolean arriving as 1; a nested object arriving as a map.
  `Data.n` raises an existence error, and `Data.get(xs)[1]` is a syntax error.
- Outputs: integers, 0/1, strings (including an escaped quote), lists, and a
  two-dimensional array written as a list of rows.
- Constraints: `::` with a range and a value list, `notin`, the arithmetic
  operators and functions in the table, `#~ #/\ #\/ #^ #=> #<=>`, reified sums,
  `count/2` in an expression, `count/4`, `global_cardinality/2` with `$`-pairs,
  `nvalue/2`, `all_different/1`, `all_distinct/1`, `all_different_except_0/1`,
  `element/3`, `element0/3`, `matrix_element/4` over a list of lists and over an
  array, `table_in/2`, `table_notin/2`, `regular/6`, `increasing/1`,
  `increasing_strict/1`, `decreasing/1`, `lex_le/2`, `lex_lt/2`, `circuit/1`,
  `subcircuit/1`, `cumulative/4`, `serialized/2`, `diffn/1`, `cond/3`, and
  `util`'s `transpose/1`.
- Traps: `X + Y` in an output value, and `[X2 + 5, Y2 + 7]` as a global
  constraint's argument, raise `instantiation_error`; so does
  `[W[I] * X[I] : I in 1..N]` bound to a variable or given to
  `all_different/1`, while the same comprehension inside `sum(...) #= 5` or
  inside `$max(sum(...))` is kept as a term and solves; `L[I]` with `I` a domain
  variable raises `type_error(integer, ...)`; `X = X + 1` makes the model fail;
  a variable introduced inside a `foreach` body takes a different value in each
  iteration; a global constraint under `#\/` raises `invalid_constraint_exp`;
  an output left without a domain raises `dvar_expected` under cp and
  `free_var_not_allowed` under sat.
- Objectives: `$min(...)` and `$max(...)` over a variable and over an
  expression, under both modules, reach the optimum the reference reports.
