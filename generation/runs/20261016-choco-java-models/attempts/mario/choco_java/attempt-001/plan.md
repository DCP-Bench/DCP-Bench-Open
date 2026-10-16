Mario needs to collect as much gold as possible by visiting different houses.
  -> maximise gold collected (objective, IntVar gold = scalar(visited, goldInHouse))
He starts at Mario's house and ends at Luigi's house.
  -> succ[luigi] = mario (fixed arc closes the route), subCircuit(succ, 0, length) with 0 and 1 always in the cycle
Each house has a certain amount of gold.
  -> visited[i] = (succ[i] != i) as BoolVar; gold = sum goldInHouse[i] * visited[i]
the travel between houses consumes fuel.
  -> fuel[i] = element(arc_fuel[i], succ[i]) (value of the arc used out of house i; 0 if skipped since arc_fuel[i][i] = 0)
Mario has a limited amount of fuel.
  -> sum(fuel) <= fuelLimit
plan his route to maximize the gold collected without exceeding the fuel limit.
  -> maximise gold, sum(fuel) <= fuelLimit
s[i] is the house succeeding to the ith house, s[i]=i if not part of the route.
  -> output "s" = succ; subCircuit makes skipped nodes self-loops
