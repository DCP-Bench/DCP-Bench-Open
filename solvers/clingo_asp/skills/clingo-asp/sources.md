# Sources for `clingo-asp`

Documentation this skill's instructions were written from. Add an entry
whenever a claim here comes from a specific page or version.

- <https://potassco.org/clingo/python-api/current/clingo/> — clingo Python API, accessed 2026-09-14
- <https://potassco.org/doc/start/> — Potassco guide, accessed 2026-09-14
- <https://github.com/potassco/clingo> — clingo 5.8.2, the version pinned in the image

Checked by running clingo 5.8.2 rather than taken from documentation alone:

- `#script(python)` raises "python support not available" in the pip wheel, so a
  submission cannot execute Python. That is why the integration's readiness
  isolation check drives the image directly instead of through a submission.
- Solving with `yield_=True, async_=True` and `handle.wait(seconds)` gives a real
  time limit; `handle.cancel()` then reports `result.interrupted`.
- In `optN` mode a program with an objective streams improving models and marks
  only the optimal ones with `optimality_proven`, while a program without an
  objective reports an empty `cost`. The runner uses exactly that to tell the two
  apart, so it never reports success on an unproven optimum.
- Shown symbols come back as `SymbolType.Number`, `SymbolType.String` or
  `SymbolType.Function` (which is how `true` and `false` arrive).
