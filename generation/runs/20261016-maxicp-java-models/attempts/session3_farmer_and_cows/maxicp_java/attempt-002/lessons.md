# session3_farmer_and_cows, maxicp_java

Attempt 002 is the retained model. Earlier work on this problem, for the record:

- Attempt 001 (cow-major Booleans, `notGiven`) was stopped during evaluation and has no evaluation.json.
- Check of 002 with cow-major `x[i][s]` Booleans, branched on the 0 side first: the 81-cow instance (json:1) hit `execution_timeout` (180 s, no solution). The 25-cow example was fine.
- Same encoding with son-major registration order: still `execution_timeout` on json:1.
- `notGiven[i][s]` Booleans with `x = not(notGiven)` views, son-major, largest cow first: all 5 instances accepted. json:1 took about 3.5 s, the example about 1.2 s. The value order matters: the first branch gives a cow to the son, which takes large cows first and reaches a fitting partition quickly.
