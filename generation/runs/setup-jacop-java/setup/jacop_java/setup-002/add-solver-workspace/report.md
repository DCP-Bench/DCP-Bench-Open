# add-solver report: jacop-java

- **Skill**: `solvers/jacop_java/skills/jacop-java/` (SKILL.md 175 lines, 3 runnable examples, sources.md, evals/evals.json)
- **Depth**: thorough (one independent toy-test round). This took longer than solver-setup's 30-minute default budget, which I chose to exceed.
- **Interface**: JaCoP's native Java API, as the user asked for "jacop" and Java is the API its developers ship and document.
- **Decision on existing skills**: none found. `npx skills find jacop` returned only unrelated skills by a user called "jacopen". A GitHub code search for SKILL.md files mentioning JaCoP found nothing. jacop.eu did not respond, so no llms.txt was found.
- **Tested version**: JaCoP 4.10.0, org.json 20250517, Temurin JDK 21.0.8, inside `dcp-eval/jacop_java:v1`. Nothing was installed on the host.
- **Validation**: `skills-ref validate` passed; `generation.skills validate --project` passed; `check_assets.py` passed 3/3 inside the image.

## Toy tests, round 1 (fresh agent, skill and problem.md only)

`round-1/results.txt`: **18/18 passed**.

| Problem | Instances | Result |
|---|---|---|
| n-queens | n3 (infeasible), n4, n8 | PASS |
| n-queens-all | n6 (4), n8 (92) | PASS |
| knapsack | small (15), p01 (309) | PASS |
| knapsack-all-optimal | ties, unique, fourteen | PASS |
| graph-colouring | petersen, cycle6, k4-tail | PASS |
| cryptarithm | send-more-money, two-two-four, ab-ab-aaa | PASS |
| jobshop | small (11), ft06 (55) | PASS |

The test agent hit no compile or runtime errors.

## Known gaps

These are the test agent's minor notes. They are not fixed, because any edit would need another test round:

- The skill does not say that single-file source mode allows a class name that differs from the file name.
- It gives no tip for counting distinct values. The test agent used the maximum colour index for graph colouring; whether JaCoP has an NValue constraint was not checked.
- It has no example of `Alldifferent` over shifted expressions such as queen diagonals. The agent used `XplusCeqZ` auxiliaries.
- It does not say whether a listener fires on the improving solutions found during branch and bound.
- The enumeration phase in `assets/all-optimal` sets no time limit.

## Related skills

None.
