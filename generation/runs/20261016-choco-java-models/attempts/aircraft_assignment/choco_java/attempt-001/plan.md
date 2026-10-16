# aircraft_assignment plan (attempt-001)

Variables: allocation[i][j] = number of aircraft of type i on route j, 0..availability[i].
- "each aircraft type has a limited number of available units" -> sum over routes j of allocation[i][j] <= availability[i] -> m.sum over the row, "<="
- "each route has a passenger demand that must be satisfied" -> sum over types i of allocation[i][j] * capabilities[i][j] >= demand[j] -> m.scalar(column, capabilities column, ">=", demand[j])
- "minimize the total operational cost" -> total = sum allocation[i][j] * costs[i][j] -> m.scalar(all cells, costs, "=", total); setObjective MINIMIZE total
- Outputs: allocation (IntVar[types][routes]).
