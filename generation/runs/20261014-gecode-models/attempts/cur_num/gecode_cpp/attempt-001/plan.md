# Plan: cur_num (attempt-001)

Requirement 1: "The number 48 has this peculiarity" -> the peculiar number is in 1..10000 -> IntVar peculiar(*this, 1, 10000)
Requirement 2: "Print another number" -> the answer is not 48 -> rel(*this, peculiar, IRT_NQ, 48)
Requirement 3: "if you add 1 to it the result is a square number" -> root*root == peculiar + 1, root in 1..101 (101^2 > 10001) -> rel(*this, root * root == peculiar + 1)
Requirement 4: "its half" (the half is a whole number, so the number is even) -> half in 1..5000, peculiar == 2 * half -> rel(*this, peculiar == 2 * half)
Requirement 5: "if you add 1 to its half, you also get a square number" -> root_half*root_half == half + 1, root_half in 1..71 (71^2 > 5001) -> rel(*this, root_half * root_half == half + 1)
Branching: decide peculiar first, then half, root, root_half (all decision variables branched, so no auxiliary is left open) -> branch(*this, peculiar, INT_VAR_NONE(), INT_VAL_MIN()) and the others with INT_VAR_SIZE_MIN().
Objective: none (satisfaction).
Output: peculiar (int).
