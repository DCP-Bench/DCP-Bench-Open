# Sources for `clingo-asp`

Tested with clingo 5.8.2 (pip wheel, MIT licence), Python 3.12.11, Linux, inside the image `dcp-eval/clingo_asp:v1`. The skill itself is unpinned.

Existing skills: the previous DCP-Bench integration skill for clingo_asp, which this version replaces. No external skill was searched for in this refactor.

- <https://potassco.org/clingo/> — installation (`pip install clingo`), links to the Python API and the guide
- <https://docs.potassco.org/clingo/python-api/current/> — `Control`, `SolveResult`, `Model`, `Symbol`, solve handles and `cancel`/`wait`
- <https://potassco.org/guide/> — Potassco guide; chapters on the language (<https://potassco.org/guide/language/>) and basics (<https://potassco.org/guide/basics/>)
- <https://potassco.org/guide/options> — command-line options such as `--models`, `--opt-mode`, `--project`, `--seed`, `--threads`
- <https://github.com/potassco/clingo> — the clingo project, version 5.8.2

Verified by running in the image: `#show` arity filtering and `#show.`; `project = "show"` removing projection duplicates (20 to 4 in the subset example); `opt_mode = "optN"` with `optimality_proven` marking the optima (two tied optima); `#maximize` reporting a negated cost (-3 for value 3); `/` truncating toward zero and modulo `\`; `#const` and `-c n=5` working, and `-c N=5` failing; `#script(python)` refused with "python support not available"; tab and `\uXXXX` string escapes refused, and `\"`, `\\`, `\n` accepted; capital-initial fact `_SHIP(1).` refused; `#sum` compared to `#sum` refused; `#max` over an empty set printing `info: tuple ignored: #inf@0`, and the unconditional element `0,none ;` removing it; `handle.wait` plus `handle.cancel` giving `interrupted`; `#count`, `#min`, `#max` on integers; errors raised as `RuntimeError` with messages on stderr; an interpreter exit code 139 when a configuration value is read from a temporary `Control`. The Quick start and every example in `assets/` were run in the image and their output checked by hand or by a second enumeration.

Refactored from the DCP-Bench integration skill; examples verified inside the dcp-eval/clingo_asp:v1 image.

Round 2 (fixes from the independent toy test): verified in the image with clingo 5.8.2. Aggregate elements are sets of tuples: `#sum { V : b(I,V) }` over `b(1,5). b(2,5). b(3,7).` gives 12, `#sum { V,I : ... }` gives 17, `#count { V : ... }` gives 2, and `#sum { 1 : a(X) }` over `a(1). a(2).` gives 1. `opt_mode = "optN"` with the default `models = 1` yields an unproven model and then a proven optimum as the last model (cost -4 on a 4-way tie), while `models = 0` yields every optimal model. Without `opt_mode` the single model is unproven. Strings: `letter("S")`, `atom.arguments[0].string`, and `<` on strings in the cryptarithm example, with `#sum` over negative weights compared with `!= 0`.

Independent toy test (add-solver toy problems, solved from the skill alone by a fresh tester, run in the image): 18/18 instances passed, from the results file in the skill-refactor scratch workspace. The table, run before and after the round-2 fixes:

| Problem | Instance | Result |
|---|---|---|
| cryptarithm | ab-ab-aaa | PASS (infeasibility reported) |
| cryptarithm | send-more-money | PASS |
| cryptarithm | two-two-four | PASS |
| graph-colouring | cycle6 | PASS (optimal 2) |
| graph-colouring | k4-tail | PASS (optimal 4) |
| graph-colouring | petersen | PASS (optimal 3) |
| jobshop | ft06 | PASS after the round-2 repair (first run: timeout after 120 s) |
| jobshop | small | PASS (optimal 11) |
| knapsack | p01 | PASS (optimal 309) |
| knapsack | small | PASS (optimal 15) |
| knapsack-all-optimal | fourteen | PASS (9 optimal) |
| knapsack-all-optimal | ties | PASS (5 optimal) |
| knapsack-all-optimal | unique | PASS (1 optimal) |
| n-queens | n3 | PASS (infeasibility reported) |
| n-queens | n4 | PASS |
| n-queens | n8 | PASS |
| n-queens-all | n6 | PASS (4 solutions) |
| n-queens-all | n8 | PASS (92 solutions) |

Total: 18/18 passed (first run 17/18; the jobshop ft06 timeout was fixed by using `models = 1` with `optN`).
