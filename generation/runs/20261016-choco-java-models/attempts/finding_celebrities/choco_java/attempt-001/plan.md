Problem: a celebrity is known by everybody else at the party and knows only other celebrities; output 0/1 per person.
Everybody at the party knows the celebrity (every other guest knows him/her) -> precomputed from the graph: celebrity[i] = 0 if some other guest j does not know i
A celebrity knows only other celebrities -> for each j != i with knows[i][j] = 1: the (not celebrity[j]) count over those guests is 0
A person is a celebrity exactly when both conditions hold -> celebrity[i] <=> (sum of not-celebrity over the guests i knows = 0)
At least one celebrity is present -> sum of celebrity >= 1
Objective: none (satisfaction); output celebrities
