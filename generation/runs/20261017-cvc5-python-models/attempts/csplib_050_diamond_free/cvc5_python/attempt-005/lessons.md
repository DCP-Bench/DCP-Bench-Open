# Lessons: csplib_050_diamond_free, cvc5_python

- Attempt 1 was evaluated with the old run profile (1 instance, solution limit 1). Coverage was not meaningful, so it was not counted and was redone as attempt 2.
- Attempt 2 (Sum-of-Booleans degree and diamond counts, inline degrees): accepted, but 2/6 instances checked. N=11 and N=13 timed out at 180 s.
- Attempt 3 (explicit Int degree variables tied by equality rows): same 2/6 coverage. Explicit degrees alone did not help.
- Attempt 4 (diamond as pure clauses: each 5-subset of a four-set's pairs must contain a missing edge; inline degree sums): accepted, 4/6. N=13 and N=15 timed out.
- Attempt 5 (clause diamond encoding plus explicit degree variables): accepted, 5/6 (0.83). Only N=15 (json:5) timed out at 180 s. Retained.
- The clause encoding of the diamond condition was the change that mattered. Counting sums of Booleans were slow for cvc5 at N >= 11.
- Reading of the description: "modulo 3" is taken as degree divisible by 3, and "sum of the degrees modulo 12" as the sum divisible by 12. Degrees are 3, 6, 9, ... up to N - 1.
