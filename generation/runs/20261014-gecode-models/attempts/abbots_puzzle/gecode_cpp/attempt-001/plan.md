Problem: 100 bushels of corn among 100 people; each man gets 3 bushels, each woman 2, each child 0.5; women are five times the men. Find men, women, children.

- 100 bushels distributed among 100 people -> linear(IntArgs({1,1,1}), {men,women,children}, IRT_EQ, 100) [people count]
- each man 3 bushels, each woman 2, each child half a bushel, all 100 bushels used -> linear(IntArgs({6,4,1}), {men,women,children}, IRT_EQ, 200) [twice the bushel sum, so the half bushel is an integer coefficient]
- there are five times as many women as men -> linear(IntArgs({1,-5}), {women,men}, IRT_EQ, 0) [women - 5*men = 0; weighted count]
- each count between 0 and 100 -> domains of the three IntVar members, 0..100 (problem bound: at most 100 people)
- branching: INT_VAR_SIZE_MIN over the three counts, INT_VAL_MIN (3 variables, all decisions)
- objective: none (satisfaction); outputs children, men, women
