# Setup notes: jacop_java (setup-002)

The setup skill (`rosetta-skills/solver-setup`, commit ca80fb092) was frozen by `generation.manage setup-attempt` before any integration file was written. add-solver came from `skills/add-solver/` in this repository.

`setup-001` was an empty directory. The first `setup-attempt` call created it, then crashed because PyYAML was missing from `.venv`. I installed `requirements.txt` into `.venv` and reran the call. setup-001 was removed because nothing was recorded in it.

## Target and capabilities

- Solver: JaCoP 4.10.0, language Java, through JaCoP's native API.
- Capabilities: satisfaction, minimisation, maximisation, enumeration. The integration compiles (`compilation: true`).
- Image: `dcp-eval/jacop_java:v1`, ID in `image-id.txt`.
- Image contents: base `eclipse-temurin:21.0.8_9-jdk-noble` pinned by digest, python3 3.12.3-0ubuntu2.1, and JaCoP 4.10.0 plus org.json 20250517 from Maven Central, each checked against its SHA-256.

## Submission contract (chosen here)

The submission is one Java file declaring `class Submission` with `static dcp.jacop.Model build(org.json.JSONObject instance, org.jacop.core.Store store)`. Inside `build`, the model posts JaCoP's own constraints on the store. It returns a `Model` that:

- names its outputs with `put(name, IntVar | int | Boolean | arrays/collections)`;
- may call `minimize(v)` or `maximize(v)`;
- may call `search(order, comparator, indomain)`.

The harness (`solvers/jacop_java/java/dcp/jacop/`) is compiled into the image. It does the following:

- It points `System.out` at stderr while the submission runs.
- It labels the model's order first, then the outputs, then every other `IntVar` in the store, so no variable is left unfixed. With no order given, it uses `SmallestDomain`/`IndomainMin`.
- It proves the optimum before emitting. A maximised objective is minimised through a negated variable.
- It enumerates by re-solving the same store one level above the base. Each time it blocks the emitted output tuple and fixes the objective at the optimum.

**JaCoP pitfall found and fixed:** JaCoP does not keep a constraint imposed between searches if that constraint is first found satisfied inside a search level. Readiness caught this: minimisation with 3 solutions produced a suboptimal third solution. The harness now calls `store.consistency()` at the base level before the first search and after every imposed blocking or objective constraint (evidence: `add-solver-workspace/probes/relevel.txt`).

**Gap:** the standalone skill carries no submission-contract text, by solver-setup's rule. The contract lives only in the harness Javadoc, `tests/fixtures/model_jacop.java`, `readiness_test.py` and this note. model-generator's procedure does not say where a modeller reads it.

## Commands and results

- `python -m evaluation.build jacop_java`: image built.
- `python solvers/jacop_java/readiness_test.py`: 14/14 checks passed.
- `python -m generation.readiness check --solver jacop_java --output solvers/jacop_java/readiness.json`: recorded.
- `python rosetta-skills/solver-setup/scripts/check_integration.py jacop_java`: 42 passed, 0 failed.
- `DCP_CONTAINER_TESTS=1 python -m unittest tests.test_solvers -k pilots -k maximization -k certified -k readme`:
  - All jacop_java subtests passed.
  - The 51 failures belong to the 17 other integrations, whose images are not built on this machine (`infrastructure_error`, no such image).
- Toy tests: 18/18 (`add-solver-workspace/round-1/results.txt`).

## Limitations

- Only integer outputs are supported: IntVar, int, Boolean, or nested arrays of these. There are no set or float variables.
- JaCoP checks its timeout between search nodes. The outer guard in run.py is the execution timeout plus 5 s.
- The isolation, timeout and missing-image checks pass.

## Also present in this repository

An older, unmerged branch, `add-jacop-solver` (commit 8b95a227d, 2026-10-01), holds a separate integration with id `jacop`. It was made under the previous solver-setup procedure. It uses the same fixture filename, `tests/fixtures/model_jacop.java`, so the two branches conflict if both are merged. A local image `dcp-eval/jacop:v1` belongs to it.
