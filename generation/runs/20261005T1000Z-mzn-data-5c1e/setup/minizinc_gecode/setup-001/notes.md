# minizinc_gecode: binding ragged and mixed-type instance fields

## What changed

- `solvers/minizinc_gecode/run.py` reshapes instance fields before they reach
  MiniZinc's data interface, then calls `runtime.minizinc_solver` unchanged.
  It replaces `runtime.minizinc_solver` on the module and calls `runtime.main`,
  so request parsing, the time budget, statuses and error handling are
  `runtime.main`'s own. A refusal raises inside `main` and becomes an `error`
  status whose detail names the field. `runner/runtime.py` is untouched.
- Binding rules (all arrays 1-based, as MiniZinc indexes a JSON array):
  1. A field MiniZinc accepts binds unchanged. A nonempty list of lists also
     gets `<field>_len`, unless an instance field already has that name.
  2. A ragged list of rows with one item shape and one scalar kind binds as
     `<field>` padded to the longest row (0, false, 0.0, ""), plus
     `<field>_len`. Items may be equal-shape arrays (jobshop: 3-D).
  3. Equal-length rows whose columns differ in kind (string / number / array)
     bind as `<field>_1`, `<field>_2`, ...; `<field>` is not bound. Each column
     binds by rule 1 or 2, never split again.
  4. Anything else ragged or mixed is refused, as is a generated name that is
     already an instance field or is generated twice.
  "Kind" follows what MiniZinc accepts: Booleans, ints and floats mix in one
  array; strings and numbers do not.
- `metadata.yaml`: `instance_binding` from `rectangular_uniform` to `any`, so
  `generation.next_work` no longer withholds these pairs. No generation code
  changed.
- `generation/blockers.json` is not changed here; it is the coordinator's.
  Its covering_opl and session2_movie_scheduling entries for minizinc_gecode
  describe the limit this change removes and still withhold those two pairs.
  kakuro / minizinc_gecode needs an entry: rule 4 refuses its `problem` field
  (a sum followed by a variable number of cells: ragged and mixed at once) on
  all five listed instances, see `real-instance-binding.log`.
- `readiness_test.py`: added `ragged_field`, `mixed_type_rows`,
  `unbindable_field_refused`; every earlier check kept.
- Skill: binding section with four worked examples in `SKILL.md`, entries in
  `sources.md`, eval `reshaped-instance-fields`.
- Readiness record archived to
  `solvers/minizinc_gecode/readiness/superseded/readiness-before-ragged-binding.json`
  and re-recorded.

## Why rule 1 adds `<field>_len` to rectangular fields

The approved rule supplies `<field>_len` only for ragged fields. Measured on the
dataset: kenken `json:1` has every cage of two cells, so `problem_2` is
rectangular there; jobshop `json:1`, `json:2`, `json:4` have equal-length jobs.
Without rule 1's `_len` a model declaring `problem_2_len` or `jobs_data_len`
fails with an unassigned parameter on those instances. An undeclared bound name
is ignored by minizinc-python 0.10.0 / MiniZinc 2.9.3 (measured), so retained
models that do not declare it are unaffected; see the regression below.

## Evidence

- `build.log`: `evaluation.build minizinc_gecode`, exit 0.
- `readiness-dryrun-*.{stdout,stderr}`, then `generation.readiness check`
  (`readiness-check.log`) and `verify` (`readiness-verify.log`). Evidence is
  kept in `solvers/minizinc_gecode/readiness/`.
- `real-instance-binding.log`: parameter-only models (declarations plus a
  probe output, no benchmark model) run directly on the image for all five
  listed instances of the eight reshaped problems: all bound and returned
  `limit`; kakuro refused on all five with the rule-4 message.
- `negative-control.log`: the ragged readiness model changed to read the
  padded width instead of `rows_len` is rejected (`invalid_solution`).
- `regression-retained-models.log`: the 41 retained minizinc_gecode models
  whose binding gains a `_len` key, re-evaluated on every instance with
  `tolerate_inconclusive` off: 36 accepted; 5 stopped at `execution_timeout`.
  Those 5 were retained with `tolerate_inconclusive`; `regression-tolerant.log`
  re-runs them that way and all 5 are accepted, timing out on the instances
  their records already list, plus csplib_001_car_sequencing json:16.
  That instance took 50.4 s under the 180 s budget at retention; at the 60 s
  default it times out, and at 180 s it is accepted in 62.6 s
  (`regression-car-sequencing-json16.log`, run while other agents' containers
  shared the machine). The difference is budget and load, not binding.
- `container-tests.log`: `tests/test_solvers.py` ContainerTests
  `test_minizinc_satisfaction`, `test_maximization`, `test_pilots` (PILOTS
  narrowed to minizinc_gecode by the harness) and `test_missing_image`, with
  `DCP_CONTAINER_TESTS=1`: OK. `unit-tests.log`: MetadataTests, test_readiness,
  test_generation unpatched: 47 OK.
- `skill-validate.log`: `generation.skills validate --project`, exit 0.
- `next-work.json`: minizinc_gecode ready, `instance_binding: any`,
  `unbindable_pairs` empty. Eligible: cabling, csplib_022_bus_driver_scheduling,
  csplib_057_killer_sudoku, jobshop, kenken, session3_kidney_exchange, and
  kakuro (which run.py refuses). covering_opl and session2_movie_scheduling stay
  withheld by their blockers.json entries until the coordinator removes them.

## Not verified

- No benchmark model was written for the eight pairs, so no evaluator
  acceptance on them exists yet; only the binding is evidenced.
- The behavioural eval `reshaped-instance-fields` was not run by an agent.
- `generation.brief` still lists these fields under `unbindable_fields` with a
  note about rectangular binders; it is solver-independent and was not changed.
- Tuples in an embedded example (jobshop) are lists by the time they reach the
  container (JSON request); run.py does not handle tuples itself.
