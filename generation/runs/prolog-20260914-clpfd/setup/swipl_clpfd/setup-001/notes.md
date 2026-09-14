# Setup: `swipl_clpfd`

SWI-Prolog with `library(clpfd)`, the first Prolog integration in this
repository and the first one whose search is the language's own backtracking
rather than a solver object the runner drives.

## Files created

| Path | What it is |
| --- | --- |
| `solvers/swipl_clpfd/metadata.yaml` | integration metadata, same key set as the others |
| `solvers/swipl_clpfd/run.py` | image entrypoint: owns the process, the budget and the protocol |
| `solvers/swipl_clpfd/driver.pl` | solving side: consults the submission, labels, optimises, enumerates |
| `solvers/swipl_clpfd/Dockerfile` | `swipl:9.2.9` plus the two runner files |
| `solvers/swipl_clpfd/readiness_test.py` | the eleven checks below, driven through the real evaluator |
| `solvers/swipl_clpfd/skills/swipl-clpfd/` | modelling skill, its sources and its behavioural cases |

Nothing outside `solvers/swipl_clpfd/` was touched: `runner/runtime.py` and
`runner/requirements.txt` are shared with the certified images and stayed as
they were.

## Versions and sources

- Base image `swipl:9.2.9`, digest
  `sha256:3e4b85b16f1e269c8a3ce3d968c843aa4cd858f7ace2db49398ec9a2b113bf0f`.
  It already carries `library(clpfd)`, `library(http/json)` and Python 3.11.2,
  so the integration installs nothing and needs no network at build time beyond
  the base image itself.
- Built image `dcp-eval/swipl_clpfd:v1`, id
  `sha256:7b0a8b7aba86b8a070408a75727b6c628038f39093476d68c22e3ea94630b6f7`.
- Documentation used is listed in `solvers/swipl_clpfd/skills/swipl-clpfd/sources.md`;
  every API claim in the skill was additionally run inside this image.

## The design decision that shapes every model

Of the three patterns in `skills/solver-setup`, this integration uses **the
model reads the instance**: `run.py` stages nothing extra, and the driver hands
the submission the instance JSON as a SWI-Prolog dict read by
`json_read_dict/3`. Prolog has a native dict for exactly this, so neither
generating Prolog source from the instance nor binding parameters outside the
model was needed.

The submission states the model and nothing else:

    model(Instance, Vars, Outputs)               % satisfaction
    model(Instance, Vars, Outputs, Objective)    % min(Expr) | max(Expr) | none
    labeling_options(Options)                    % optional, defaults to [ff]

`driver.pl` owns labelling, optimisation, enumeration, deduplication and
printing; `run.py` owns the process, the execution budget and the protocol, and
emits exactly one status whatever the driver did — including when the driver
printed more solutions than were requested, which is refused rather than passed
on.

Optimisation rests on one documented property of `labeling/2`: under `min(Expr)`
it enumerates in ascending order of `Expr`, so its first solution is optimal.
The driver proves the optimum that way, then rebuilds the model with the optimum
fixed and enumerates only assignments that achieve it. A run that never reaches
that first solution reports `timeout`, never a result.

## Readiness

`python -m generation.readiness check --solver swipl_clpfd` ran
`solvers/swipl_clpfd/readiness_test.py` against the built image; the record is
`solvers/swipl_clpfd/readiness.json` and the evidence is in
`solvers/swipl_clpfd/readiness/`. All eleven checks passed:

`satisfaction`, `changed_instances`, `enumeration`, `exhausted_enumeration`,
`minimization`, `maximization`, `isolation`, `malformed_output`, `empty_output`,
`timeout_cleanup`, `missing_image`.

`exhausted_enumeration` is beyond the required set: asking for five solutions of
a model that has exactly three must come back as three solutions with status
`complete`, which is the part of the protocol a backtracking search is most
likely to get wrong. `isolation` asserts, from inside the container, the
unprivileged uid, the absent dataset, the two staged files, the read-only root
and the unreachable network.

## Known limits

- No compilation step, so `compilation: true` is not declared and the
  `compilation_error` check does not apply.
- CLP(FD) propagation is weaker and slower than CP-SAT's; expect
  `execution_timeout` on the larger CSPLib instances where Gecode also struggles.
  That is a performance limit of the integration, not a protocol gap.
- Only one submission file is staged, so a model cannot ship a helper module.
