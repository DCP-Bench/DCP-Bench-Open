Plan (unary encoding, each count is 1 + sum of ordered Bools):
We're going out to dinner taking 1-6 grandparents -> grandparents g = 1 + sum(gs), gs = 5 ordered Bools (unary), bounds from literal count
1-10 parents -> parents p = 1 + sum(ps), ps = 9 ordered Bools (unary)
and/or 1-40 children -> children c = 1 + sum(cs), cs = 39 ordered Bools (unary)
There must be 20 total people at dinner -> g + p + c == 20
Grandparents cost $3 for dinner, parents $2 and children $0.50 -> costs in half-dollars: 6g + 4p + c
it must cost $20 -> 6g + 4p + c == 40
How many grandparents, parents and children are going to dinner -> outputs grandparents, parents, children
Objective: none (satisfaction)
