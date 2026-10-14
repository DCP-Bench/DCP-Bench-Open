Problem: age_changing. Find my age m and husband's age h (both integers, ages >= 0).

Requirement 1: starting with my age, apply the four operations (+2, /8, -3, *7) each once, in some order, and the result is h.
  -> p[0..3] is a permutation of the four operations (distinct(*this, p, IPL_DOM)); chain a[0]=m, a[k+1] = op(p[k], a[k]) with extensional over (op, before, after) triples.
Requirement 2: starting with his age, apply the same four operations in a different order and get my age m.
  -> q[0..3] permutation; chain b[0]=h, b[k+1] = op(q[k], b[k]), b[4] = m.
Requirement 3: "a different order" -> the two sequences differ in at least one position.
  -> diff_k = expr(p[k] != q[k]) (BoolVar); linear(diff, IRT_GQ, 1).
Requirement 4: "/8" applies to whole ages: exact division (value must be divisible by 8). Encoded in the operation table: /8 only for multiples of 8.
Requirement 5: ages are non-negative; -3 requires a value >= 3. Domains 0..2000 for chain values.
  -> the operation table excludes values outside the domain.
Branching: ops p and q (smallest domain first), then m and h, then the chain values.
Objective: satisfaction.
