# csplib_003_quasigroup_existence (QG3.m)

Find an order-m quasigroup (a Latin square on 0..m-1) with the QG3 property
(a*b)*(b*a) = a.

- Instance input: `m`.
- Output: `quasigroup` — m x m matrix of integers in 0..m-1.
- Satisfaction. Constraints: every row and every column is all-different;
  quasigroup[quasigroup[a, b], quasigroup[b, a]] = a for all a, b.
