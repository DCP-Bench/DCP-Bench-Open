# csplib_003_quasigroup_existence (QG3.m)

An order-m quasigroup (Latin square on 0..m-1) with (a*b)*(b*a) = a.

- Instance input: `m`. Output: `quasigroup` — an m x m matrix of 0..m-1.
- Satisfaction. Rows and columns all-different, plus the QG3 property.
- The reference times out on m >= 12, so only the first four instances are
  reachable for any model of this problem.
