Mario must visit houses on a route from Mario's house to Luigi's house, collecting gold
Each house has gold; the route's arc fuel total must stay within the fuel limit
s[i] is the house after house i on the route, s[i] = i if house i is not on the route; s[Luigi] = Mario's house
-> succ is an IntVarArray of n vars, domain 0..n-1, one output "s"
s[i] = i if not part of the route -> optional nodes; Gecode circuit has no self-loops. Decomposition (no row fits, subcircuit is not in the map):
  distinct(*this, succ, IPL_DOM) [successor array is a permutation; self-loops are distinct values]
  succ[Mario] != Mario -> rel(*this, succ[m] != m)
  succ[Luigi] = Mario -> rel(*this, succ[l] == m)
no route can close without Mario (subtour elimination) -> ord[i] in 0..n-1 position on the route, ord[Mario] = 0 (rel)
  (succ[i] == i) or (succ[i] == Mario) or ord[succ[i]] == ord[i] + 1 -> element(ord, succ[i], t[i]) + rel with ||
  unvisited house has ord 0 (removes symmetric ord values for the search)
  Map row justification: circuit (row "visit every node once") is for a full tour only.
fuel: sum over houses of arc_fuel[i][s[i]] <= fuelLimit -> element(IntArgs(row_i), succ[i], f_i) (self loop costs 0: diagonal set to 0 in the row copy) + linear(f, IRT_LQ, fuelLimit)
gold: visited_i = (s[i] != i); total gold = sum goldInHouse[i] * visited_i -> expr(succ[i] != i) BoolVars + linear(IntArgs(gold), visited, IRT_EQ, total)
branching: succ with INT_VAR_SIZE_MIN, INT_VAL_MIN; then ord and t (fixed by propagation)
objective: maximize total gold
