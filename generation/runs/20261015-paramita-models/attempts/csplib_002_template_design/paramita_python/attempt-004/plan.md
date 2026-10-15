Print the number of printed sheets (production) for each template -> production[t] = sum_j 2^j * b[t][j], binary bits b per template, 0 <= production <= max demand (a sheet count above the largest demand is never needed)
The layout of the templates (layout), each inner list is the number of each variation on that template -> layout[t][v] = sum_k k * L[t][v][k], one-hot L[t][v][k] for k = 0..n_slots, exactly one per (t,v)
A template holds at most n_slots variations (mother sheet slots) -> sum over v of layout[t][v] <= n_slots, PB with small weights
Each variation's demand is met by the printed sheets -> for each v: sum over t,k,j of k * 2^j * M[t][v][k][j] >= demand[v], with M[t][v][k][j] <-> (L[t][v][k] and b[t][j]) (one-hot times binary, aux per (copies value, bit))
Templates are interchangeable: order them by sheet count -> production[t] >= production[t+1] (symmetry breaking, keeps the optimum)
Objective: minimise the total number of printed sheets -> minimize sum_t production[t]
