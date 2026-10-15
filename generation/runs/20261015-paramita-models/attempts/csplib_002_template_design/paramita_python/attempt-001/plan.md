# Plan: csplib_002_template_design (paramita_python)

- Each template holds n_slots variations: copies of variation i on template t = layout[t][i]; one-hot over 0..n_slots -> layout = sum v * bit.
- Each template has n_slots printed items in total: sum_i layout[t][i] == n_slots (PB, equality; padding never hurts the optimum).
- Each variation's demand is met: sum_t production[t] * layout[t][i] >= demand[i]. Product: production[t] unary (ge_p = production >= p, p in 1..max demand); q_k(t,i) = (layout[t][i] * production[t] >= k) for k in 1..demand[i], as Iff with an Or over v of (layout = v and production >= ceil(k/v)); then sum over t,k of q_k >= demand[i] (PB over capped values).
- Objective: minimise total sheets = sum_t sum_p ge_p(t).
- Symmetry: templates are interchangeable, so sheets(t) >= sheets(t+1).
- Redundant: n_slots * total sheets >= total demand (implied by the slot and demand constraints).
