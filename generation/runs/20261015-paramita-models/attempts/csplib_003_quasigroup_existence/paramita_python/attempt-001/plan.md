# Plan: csplib_003_quasigroup_existence (paramita_python)

- Product a*b = c: one-hot Bools x[a][b][c] (exactly one c per cell) -> quasigroup[a][b] = sum c * x[a][b][c].
- Every row contains each element once: for each row a and value c, sum_b x[a][b][c] == 1.
- Every column contains each element once: for each column b and value c, sum_a x[a][b][c] == 1.
- QG3 identity (a*b)*(b*a) = a: for all a, b, c, d: (a*b = c and b*a = d) -> c*d = a, i.e. If(And(x[a][b][c], x[b][a][d]), x[c][d][a]).
- Satisfaction problem, no objective.
