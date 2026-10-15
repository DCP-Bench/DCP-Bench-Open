How many distinct templates / which variations, and how many copies of each, on each template -> n_templates given; layout[t][v] = sum 2^i * kb[t][v][i], binary Bools (3 bits), at most min(n_var, n_slots) copies (the reference's domain bound, found by probing)
Each template has n_slots slots, filled with copies of variations -> sum over v of layout[t][v] == n_slots (PB with small weights; an extra copy never hurts)
Number of printed sheets (production) for each template -> production[t] = sum 2^j * bit[t][j], binary, at most the largest demand
Each variation's demand is met by the printed sheets -> sum over t,i,j of 2^(i+j) * m[t][v][i][j] >= demand[v], m -> (kb[t][v][i] & bit[t][j]) (one direction, m only helps a >= constraint)
Redundant: all sheets together carry at most n_slots copies each -> sum(production) >= ceil(sum(demand) / n_slots)
Symmetry: templates interchangeable -> production[t] >= production[t+1]; variations with equal demand interchangeable -> order their copy vectors
Objective: minimise total printed sheets -> minimize sum(production)
