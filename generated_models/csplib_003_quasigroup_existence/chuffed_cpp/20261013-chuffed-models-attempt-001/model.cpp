// QG3 quasigroup existence: find an order m quasigroup (an m x m Latin square with symbols 0..m-1)
// such that (a*b)*(b*a) = a for all a and b, where a*b is the entry in row a, column b.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int m = instance.at("m");
  int cells = m * m;

  // t[i*m+j] is the product i*j, a symbol in 0..m-1 (row i, column j)
  vec<IntVar*> t;
  createVars(t, cells, 0, m - 1);

  // every row contains each symbol exactly once
  for (int i = 0; i < m; ++i) {
    vec<IntVar*> row;
    for (int j = 0; j < m; ++j) row.push(t[i * m + j]);
    all_different(row);
  }

  // every column contains each symbol exactly once
  for (int j = 0; j < m; ++j) {
    vec<IntVar*> col;
    for (int i = 0; i < m; ++i) col.push(t[i * m + j]);
    all_different(col);
  }

  // for every pair a, b: with p = a*b and q = b*a, the product p*q must equal a
  for (int a = 0; a < m; ++a) {
    for (int b = 0; b < m; ++b) {
      IntVar* p = t[a * m + b];
      IntVar* q = t[b * m + a];

      // position of (p, q) in the row-major table
      IntVar* idx = newIntVar(0, cells - 1);
      vec<int> w;
      w.push(m);
      w.push(1);
      vec<IntVar*> pq;
      pq.push(p);
      pq.push(q);
      int_linear(w, pq, IRT_EQ, idx);

      // the entry at that position is the constant a
      array_var_int_element_bound(idx, t, getConstant(a));
    }
  }

  // the table entries are the decision variables
  branch(t, VAR_INORDER, VAL_MIN);

  json rows = json::array();
  for (int i = 0; i < m; ++i) {
    json row = json::array();
    for (int j = 0; j < m; ++j) row.push_back(dcp::out(t[i * m + j]));
    rows.push_back(row);
  }
  outputs = {{"quasigroup", rows}};
}
