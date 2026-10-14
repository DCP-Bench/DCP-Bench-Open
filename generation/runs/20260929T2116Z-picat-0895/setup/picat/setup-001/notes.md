# picat setup

New integration for Picat 3.9#12, a logic-based language whose `cp` and `sat`
modules take the same constraint models. A submission imports one of them.

- Artifacts: `solvers/picat/metadata.yaml`, `Dockerfile`, `run.py`,
  `driver.pi`, `readiness_test.py`, and the skill bundle
  `solvers/picat/skills/picat/`. Wiring outside that directory:
  `tests/fixtures/model_picat.pi` with its `PILOTS` and `MAXIMIZATION_SWAPS`
  rows in `tests/test_solvers.py`, a `picat` row in `LANGUAGES` and `.pi` in
  `EXTENSION_LANGUAGE` in `generate_site.py`, and the name in `README.md`.
- Source: the official 64-bit Linux build,
  `https://picat-lang.org/download/picat39_12_linux64.tar.gz`, SHA-256
  `f053b11cccabfb69a3ccd779f2dc1c24cdf889805799bc8c779e6c56da703e4a`, on
  `python:3.12.11-slim-bookworm` pinned by digest. The Dockerfile verifies the
  hash before unpacking. Licence: free for any purpose, C sources under MPL 2.0
  (`Picat/LICENSE`).
- Image built with `python -m evaluation.build picat`:
  `sha256:59c7946aa6a99bc6f6ca146559c554b94c2ed0d1df56ba02955402fa60271966`.

## Design

- Instance binding: `run.py` writes the JSON instance as one Picat term
  (arrays as lists, objects as `json_object(Keys, Values)`, strings as Picat
  strings, `true`/`false` as 1/0) and the driver turns it into a map, so a
  model reads `Data.get(key)`.
- The driver (`driver.pi`) imports no solver. `solve/2`, `#=/2` and
  `solve_suspended/1` are reached through `call/N`, which Picat resolves at run
  time against the loaded modules, so they bind to the module the submission
  imported. Probing found that `call(solve_suspended)` (call/1 on an atom) is
  bound at compile time to the global module and fails; `call/2` with an
  option list is resolved at run time and works.
- Optimisation: the driver solves with `$min`/`$max` once, which both modules
  return only at a proven optimum, then rebuilds the model with the objective
  fixed and enumerates. An objective over an expression gets a variable equal
  to it. Enumeration dedupes on the JSON text of the declared outputs.
- Records go to a file, not stdout, so a `println` in a model is logged and
  cannot corrupt the protocol. `run.py` stops the process at the execution
  budget less one second and reports a timeout; on an error it appends what
  Picat printed, which is where a syntax error's line range appears.
- `mip` and `smt` are refused with a message: they call external solvers that
  are not installed.

## Evidence

- `probes/` holds 33 small submissions and `run_probes.py`, which runs each
  through the image with `import cp.` and again with `import sat.`;
  `probes.log` is their output. They back every constraint row and trap in the
  skill; the counts that were not obvious (`t22_more`, `t26_diffn_sub`) were
  checked against a brute-force enumeration.
- A read-only `--network=none --user=65534:65534` run of the isolation probe
  succeeds, and the same probe run as root with network reports `unsat`, so it
  fails closed.
- `pilot-probe.py` runs the `test_pilots` and `test_maximization` cases of
  `tests/test_solvers.py` for picat only: 7 solutions checked for both pilot
  modes and 1 for maximisation, as those tests require.
- Readiness passed all sixteen checks on the first certification run (the
  ten required ones plus `distinct_declared_outputs` and four `sat_*`
  repeats); the record is `solvers/picat/readiness.json`.

## Not done

- No `solvers/picat/SKILL.md` pointer: no other integration in the repository
  has one, and the skill is found at `solvers/picat/skills/picat/`.
- The behavioural cases in `evals/evals.json` are specifications; none has been
  run by an independent agent.
