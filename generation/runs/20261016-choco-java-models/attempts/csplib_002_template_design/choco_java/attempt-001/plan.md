how many distinct templates to produce -> n_templates templates, layout[t][v] and production[t] arrays (fixed by instance)
each template consists of a sheet with several variations etched, at most n_slots positions -> for each t: m.sum(layout[t], "<=", n_slots)
the number of copies of each variation printed must match its demand, which is produced across templates -> for each v: sum_t layout[t][v] * production[t] >= demand[v] (sums of m.times products)
the number of printed sheets per template is production[t] (non-negative) -> production[t] in 0..max demand
minimise the total number of printed sheets -> objective: minimise sum of production[t] (sum constraint)
implied: total sheets >= ceil(total demand / n_slots) -> arithm(totalSheets, ">=", bound) (derived from the instance)
symmetry: templates are interchangeable -> production[t] >= production[t+1]
search: layout by dom/wdeg with Luby restarts, then production in order (smallest first)
