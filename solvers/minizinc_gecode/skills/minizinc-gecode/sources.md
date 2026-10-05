# Sources for `minizinc-gecode`

Documentation this skill's instructions were written from. Add an entry whenever
a claim here comes from a specific page or version.

- <https://docs.minizinc.dev/en/2.9.3/> — MiniZinc 2.9.3 handbook, the version in the integration image
- <https://www.gecode.org/doc-latest/MPG.pdf> — Gecode, the backend the integration selects
- `runner/runtime.py` — the runner's own MiniZinc conventions: JSON data binding, the
  `objective` variable, and the unannotated solve item that lets it fix the optimum
- `solvers/minizinc_gecode/run.py` — the instance-binding rules: padded ragged rows with
  `<field>_len`, one array per column of mixed-type rows, and the refusal of other shapes

The claim about implied constraints was measured rather than assumed:
`csplib_049_number_partitioning` instance `json:3` (n = 20) reaches
`execution_timeout` with the direct translation of the reference and is accepted
once the two implied half-totals are added, both at the same execution budget.
Evidence: `generation/runs/models-20260914-vamos/attempts/csplib_049_number_partitioning/minizinc_gecode/`.

The binding rules were checked on the image, not only read from `run.py`: the
readiness checks `ragged_field`, `mixed_type_rows` and `unbindable_field_refused`
(`solvers/minizinc_gecode/readiness/readiness-result.json`), and parameter-only
models that bound every listed instance of the eight reshaped problems
(`generation/runs/20261005T1000Z-mzn-data-5c1e/setup/minizinc_gecode/setup-001/`).
That an undeclared bound name is ignored, and that numbers, Booleans and floats
mix in one array while strings and numbers do not, was measured on MiniZinc 2.9.3
with minizinc-python 0.10.0 in the same image.
