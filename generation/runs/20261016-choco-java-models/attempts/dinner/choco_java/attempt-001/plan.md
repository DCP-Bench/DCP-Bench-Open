We're going out to dinner taking 1-6 grandparents -> grandparents IntVar in [1, 6]
1-10 parents -> parents IntVar in [1, 10]
and/or 1-40 children -> children IntVar in [1, 40]
Grandparents cost $3 for dinner, parents $2 and children $0.50 -> cost in cents: 300*grandparents + 200*parents + 50*children = 2000 (m.scalar)
There must be 20 total people at dinner -> grandparents + parents + children = 20 (m.sum with "=")
and it must cost $20 -> the cents cost equation above (m.scalar "=", 2000)
How many grandparents, parents and children are going to dinner? -> output the three IntVars
Objective: none (satisfaction)
