# Plan: csplib_002_template_design (paramita_python), attempt 2

Attempt 1 (unary sheets, capped unary products) timed out in the optimisation proof on the example.
Attempt 2 keeps the same meaning with a binary sheet count and one product aux per (template, variation, copies value, bit).

- Copies of variation i on template t: layout[t][i] = sum v * copies_v, one-hot over 0..n_slots -> layout.
- Each template has n_slots items: sum_i layout[t][i] == n_slots.
- Sheets of template t: binary bits, value = sum 2^b * bit_b, at most max demand.
- Demand: sum_t layout[t][i] * sheets[t] >= demand[i]; product via aux a = (copies_v and bit_b), a <=> both: sum over t, v, b of v * 2^b * a >= demand[i].
- Objective: minimise total sheets = sum_t sum_b 2^b * bit_b.
- Symmetry: templates are interchangeable: sheets(t) >= sheets(t+1).
- Redundant: n_slots * total sheets >= total demand.
