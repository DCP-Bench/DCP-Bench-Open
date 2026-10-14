# Plan: curious_set_of_integers (attempt-001)

Requirements in the description's words:
- "The integers 1, 3, 8 and 120 form a set" -> fixed data of the problem, in the model as the array given[]; no constraint.
- "the product of any two integers is one less than a perfect square" -> for each given a, a*number + 1 is a square; the square root is a variable r_i with r_i * r_i == a*number + 1 (no global fits: a square test is a product with a fresh root variable).
- "Find a fifth number (larger than or equal to 0)" -> number in 0..max_val (the instance field bounds the search), a single IntVar.
- Set size n = 5 from the instance: four given integers plus the unknown; the model reads n and checks it equals given.size() + 1.
- "Print this number (number)" -> output("number", number).
- Branching: roots r_i first (INT_VAR_SIZE_MIN, INT_VAL_MIN), then number (INT_VAL_MIN). Satisfaction problem, no objective.
- Root bound: r_i in 0..floor(sqrt(120*max_val + 1)) + 1 (largest product is 120*max_val + 1).
