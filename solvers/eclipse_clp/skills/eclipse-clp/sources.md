# Sources for `eclipse-clp`

Tested with ECLiPSe 7.2 #13 (`eclipse.exe` from the x86_64 Linux tarball, Gecode solver 6.2.0 inside `gfd`), libraries ic, ic_global, ic_global_gac, ic_edge_finder, ic_edge_finder3, ic_cumulative, ic_mdd, gfd, branch_and_bound, timeout, listut, json.

Existing skills: none searched beyond the solver-setup run; none found for ECLiPSe when this skill was written.

Documentation pointers. The claims below were checked by running the system, not by reading these pages in this session:

- <https://eclipseclp.org/> and <https://eclipseclp.org/doc/> — distribution and documentation entry points
- <https://eclipseclp.org/doc/bips/lib/ic/index.html> — library(ic)
- <https://eclipseclp.org/doc/bips/lib/gfd/index.html> — library(gfd)
- <https://eclipseclp.org/doc/bips/lib/branch_and_bound/index.html> — `bb_min/3` and `bb_options`
- The library sources under `$ECLIPSEDIR/lib` (for example `gfd.ecl`) were searched for export lists and argument shapes, such as the `gcc{low,high,value}` specs in `gfd`.

Verified by running, each in ECLiPSe 7.2 #13:

- The ten examples in `assets/`, each with its README output.
- Error texts in the Common-issues table: ambiguous import of `alldifferent/1`, undefined procedure, `2**70` syntax error, `#<=>`/`#\/`/`#/\` syntax errors, the gfd 32-bit domain error, `bb_min` type error on a non-variable cost, `out of range` for `indomain_middle` in gfd `search/6`.
- Exact names and arities: `alldifferent/1` (ic, ic_global, gfd), `occurrences/3`, `atmost/3`, `gcc/2` (`ic_global_gac` with `gcc(Lo,Hi,Val)`, `gfd` with `gcc{low:,high:,value:}`), `table/2` (`ic_mdd` and `gfd`), `cumulative/4`, `disjunctive/2`, `circuit/1`, `element/3`, `lex_le/2`, `sorted/2`, `get_var_bounds/3`, `get_integer_bounds/3`, `get_bounds/3` (gfd), `get_domain_as_list/2`, `multifor/3`.
- `bb_options`: `report_success`, `report_failure`, `timeout`, `solutions:all`, `strategy` values, `report_timeout`.
- `timeout/3`: stops an `ic` search at 2 s; a `gfd` 100-queens `search/6` under a 2 s `timeout/3` was still running after more than 2 minutes (reproduced once; an earlier gfd magic-square N=6 run behaved the same under a 60 s limit).
- The performance table in SKILL.md: cputime inside ECLiPSe, ft06 and random job shops from an LCG, queens and magic squares as listed.

Not run, and marked as such in SKILL.md: `minimize/2`, the `largest`, `occurrence`, `most_constrained`, `max_regret` selectors, `indomain_median`, `indomain_random`, `alldistinct/1`, `ordered/2`, `nvalue/2`, `bin_packing/3`, `alldifferent_matrix/1`, `ic_sets`, the older `fd` library.

Not tested by an independent agent.
