# Sources for `exact`

Tested with Exact 2.2.1 (PyPI `exact`), Python 3.12.11, Linux x86_64 (python:3.12.11-slim-bookworm).

- <https://gitlab.com/nonfiction-software/exact> — README: Python interface, `pip install exact`, precompiled wheels for x86_64 Linux and Windows, feature list
- <https://gitlab.com/nonfiction-software/exact/-/blob/main/src/Exact.hpp> — the methods exposed to Python, with their descriptions
- <https://gitlab.com/nonfiction-software/exact/-/blob/main/python_examples> — `knapsack_tutorial` (read for the style of the examples)
- <https://pypi.org/project/exact/> — the distribution; `pip show exact` reports AGPL-3.0-only
- The pybind11 doc strings on `exact.Exact`, which are the authoritative signatures: `inspect.signature` raises `ValueError` on these bindings, so read `__doc__`.

Verified by running: every API behaviour in [references/exact-api.md](references/exact-api.md) and every example in `assets/` was run inside `dcp-eval/exact:v1` (Exact 2.2.1, Python 3.12.11). Examples are general patterns written for this skill.

- Verified by running: `toOptimum` returns `SAT` only for a proven optimum; maximisation values are negated; `hasSolution()` stays true after `TIMEOUT` and after exhaustion; `invalidateLastSol(names)` blocks projections; `encoding` accepts `log`, `order`, `onehot`.
- Verified by running: knapsack optimum proof times (60 items of 6 digits 0.07 s; 120 items of 7 digits 2.6 s; 200 items of 8 digits 25 s).

## Independent toy-test result

A separate tester, given only this skill, solved the add-solver toy problems (`n-queens`,
`n-queens-all`, `knapsack`, `knapsack-all-optimal`, `graph-colouring`, `cryptarithm`,
`jobshop`), with models written from the skill alone.

| Problem | Passed / total |
|---|---|
| cryptarithm | 3 / 3 |
| graph-colouring | 3 / 3 |
| jobshop | 2 / 2 |
| knapsack | 2 / 2 |
| knapsack-all-optimal | 3 / 3 |
| n-queens | 3 / 3 |
| n-queens-all | 2 / 2 |
| **Total** | **18 / 18** |

No repair attempts were needed. The tester read only the declared instance keys by choice;
the skill did not guide that at the time. The run used the skill as it stood before the round-2
additions (reading data, time limits, the job-shop, graph-colouring and cryptarithm examples).

