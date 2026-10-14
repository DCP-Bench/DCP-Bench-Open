Each child gets at least 1 candy -> IntVarArray x(*this, n, 1, n); the most any child needs is n (strictly increasing ratings).
Children next to each other: the one with the higher rating gets more candies -> for each adjacent pair with ratings[i] > ratings[i+1]: rel(*this, x[i], IRT_GR, x[i+1]); with ratings[i] < ratings[i+1]: rel(*this, x[i], IRT_LE, x[i+1]); equal ratings: no constraint. Pairwise rel: no global fits a chain of precedences over adjacent pairs, and the direction is known from the data, so no reification is needed.
Minimise the total number of candies -> z = expr(*this, sum(x), IPL_DOM) is the objective; minimize(z).
Branching -> branch(*this, x, INT_VAR_SIZE_MIN(), INT_VAL_MIN()) (every child's count is a decision; minimal values first give the optimum fast).
Output x (IntVarArray) and z (IntVar).
