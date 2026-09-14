# coin3_application
Instance: `denominations`, `max_amount_to_pay`. Output: `x` — how many coins of
each denomination, 0..max_amount_to_pay. Minimize the number of coins while
every amount from 1 to max_amount_to_pay - 1 can be paid exactly from the coins
held. The reference states that with a fresh auxiliary vector per amount,
bounded by x; this model does the same.
