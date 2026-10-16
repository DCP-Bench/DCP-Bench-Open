# Plan: bananas (attempt 1)

Variables: x[0] bananas, x[1] oranges, x[2] mangoes, x[3] apples, each 1..100 (all types must be bought).
Prices scaled by 315 (lcm of 5, 7, 9, 3) so every price is an integer: banana 189, orange 225, mango 245, apple 945; budget 31500.

- "100 fruits" -> linear(*this, {1,1,1,1}, x, IRT_EQ, 100)
- "100 dollars" (spent in full) -> linear(*this, {189,225,245,945}, x, IRT_EQ, 31500)
- "all types of fruits need to be purchased" -> lower bound 1 on each variable (domain 1..100)
- "bananas and apples should be of minimum quantity" -> cost = x[0] + x[3] via expr(...), minimize(cost)
- branching -> branch(*this, x, INT_VAR_SIZE_MIN(), INT_VAL_MIN())
