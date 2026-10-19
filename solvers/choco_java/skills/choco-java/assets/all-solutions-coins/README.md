# Making change (all solutions)

**Problem:** count the ways to pay 10 with any number of coins worth 1, 2 and 5.
**Shows:** enumeration with `solve()` in a loop until it returns `false`, a bounded integer per coin, `scalar` as the payment rule. The coin counts are the only decision variables, and the amount follows from them, so no solution repeats.
**Run:** `java Coins.java`
**Expected:** `Ways to pay 10 with coins [1, 2, 5]: 10`
