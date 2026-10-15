Mario needs to collect as much gold as possible by visiting different houses. -> arc[i][j] Bool per allowed arc (one-hot successor per house), gold objective over out-arcs
He starts at Mario's house and ends at Luigi's house. -> sum(out_arcs(mario)) == 1, sum(in_arcs(luigi)) == 1, unary positions along the route
Each house has a certain amount of gold. -> visited[i] <=> OR(out-arcs of i); objective sum(gold[i] * visited[i])
the travel between houses consumes fuel. -> arc_fuel[i][j] weights on arc[i][j]
Mario has a limited amount of fuel, and he needs to plan his route ... without exceeding the fuel limit. -> sum(arc_fuel[i][j] * arc[i][j]) <= fuelLimit
Print the succeeding houses for each house (s) ... s[i]=i if not part of the route. -> s[i] = i + sum((j - i) * arc[i][j]) (one out-arc at most)
For luigi's house, the succeeding house should be Mario's house. -> arc[luigi][mario] forced: sum(out_arcs(luigi)) == 1 and the only out-arc of luigi goes to mario
Route has no side loops (subtours must not form away from Mario). -> unary position pos[i][k] (k=1..n-1), arc[i][j] implies pos[j] >= pos[i] + 1, arcs into Mario excluded
Objective: maximize total gold collected -> maximize sum(gold[i] * visited[i])
