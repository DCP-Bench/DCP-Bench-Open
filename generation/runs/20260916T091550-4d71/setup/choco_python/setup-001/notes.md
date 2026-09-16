# choco_python setup

New integration for the Choco 4 constraint solver through pychoco 0.2.1.

- `metadata.yaml`, `run.py`, `Dockerfile`, `readiness_test.py` and the skill
  bundle under `skills/choco-python/` are the artifacts.
- The wheel bundles Choco's native library, so the image is plain
  `python:3.12.11-slim-bookworm` with no JVM.
- API probes are `api-probe-1.py` and `api-probe-2.py`; the first found that
  `sum_`, `min_` and `max_` do not exist (they are `sum`, `min`, `max`), which
  corrected a first draft of the skill before any model was written.
- `limits-probe.py` established that `limit_time` stops the search at the limit
  and that pychoco exposes no exhaustion flag, which is why `run.py` tells
  exhaustion from timeout by elapsed time with a 0.5s margin.
- Readiness passed all ten required checks on the first run; the record is
  `solvers/choco_python/readiness.json`.
