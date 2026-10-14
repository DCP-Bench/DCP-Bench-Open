# Plan: equal_sized_groups (gecode_cpp, attempt-001)

Variables: x[i] (i = 0..K-2) = 1-based index of the last element of group i+1; x in 1..N-1. Group sizes from x with x_0 = 0 and x_K = N.

Requirements:
- "I have a sorted list of N elements, and I want to divide them into K groups, by choosing K-1 split points between them." -> IntVarArray x(*this, K-1, 1, N-1)
- "it is necessary to have items with same value in the same group" -> dom(*this, x[i], IntSet(breaks)) with breaks = { j : a[j-1] != a[j] } (domain restriction, no propagator needed)
- "the break points" in increasing order, groups non-empty -> rel(*this, x[i], IRT_LE, x[i+1])
- "as close in size to round(N/K) as possible" -> ideal = (2N + K) / (2K) (round half up), constant from instance
- "total error = sum abs(size - ideal)" -> per group expr(*this, abs(right - left - ideal)) with left/right the neighbouring breaks or the constants 0 and N; total = expr(*this, sum(errors))
- Branching: branch on x in order (INT_VAR_NONE), smallest value first.
- Objective: minimize total.
