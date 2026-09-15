# Sources for `minizinc-gecode`

Documentation this skill's instructions were written from. Add an entry whenever
a claim here comes from a specific page or version.

- <https://docs.minizinc.dev/en/2.9.3/> — MiniZinc 2.9.3 handbook, the version in the integration image
- <https://www.gecode.org/doc-latest/MPG.pdf> — Gecode, the backend the integration selects
- `runner/runtime.py` — the runner's own MiniZinc conventions: JSON data binding, the
  `objective` variable, and the unannotated solve item that lets it fix the optimum

The claim about implied constraints was measured rather than assumed:
`csplib_049_number_partitioning` instance `json:3` (n = 20) reaches
`execution_timeout` with the direct translation of the reference and is accepted
once the two implied half-totals are added, both at the same execution budget.
Evidence: `generation/runs/models-20260914-vamos/attempts/csplib_049_number_partitioning/minizinc_gecode/`.
