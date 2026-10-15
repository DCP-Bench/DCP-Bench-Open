# Plan: devils_word

- "insert '+' or '-' operators before each integer" -> one Bool `plus_i` per array position (true = '+'), no integer encoding needed.
- "summing them up will result in total" -> `sum(2*a_i*plus_i) - sum(a_i) == total` (PB over Bools with constant offset).
- "print the array with the correct signs (result)" -> output `result_i = 2*a_i*plus_i - a_i`, an integer expression equal to +a_i or -a_i.
- objective: none (satisfaction).
