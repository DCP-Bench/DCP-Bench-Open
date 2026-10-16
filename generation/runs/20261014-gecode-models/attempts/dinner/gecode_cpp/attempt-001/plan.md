# Plan: dinner (satisfaction)

1-6 grandparents -> IntVar grandparents(*this, 1, 6)
1-10 parents -> IntVar parents(*this, 1, 10)
1-40 children -> IntVar children(*this, 1, 40)
There must be 20 total people at dinner -> linear(*this, IntArgs({1,1,1}), {g,p,c}, IRT_EQ, 20, IPL_DOM)
grandparents cost $3, parents $2, children $0.50 and it must cost $20 -> costs doubled to cents-free integers, linear(*this, IntArgs({6,4,1}), {g,p,c}, IRT_EQ, 40, IPL_DOM) (6g+4p+c = 40 is 2 x (3g+2p+0.5c = 20))
Branching -> one decision set: branch on the three counts with INT_VAR_SIZE_MIN, INT_VAL_MIN (domains are tiny, so no extra search tuning)
Objective -> none (satisfaction)
Outputs -> children, grandparents, parents, each an IntVar
