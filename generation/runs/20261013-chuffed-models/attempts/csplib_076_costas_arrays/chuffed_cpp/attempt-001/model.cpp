// Costas array: a permutation of 1..n whose difference triangle has no repeated value in any line.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("n");

  // costas[i] is the (1-based) row of the mark in column i; the marks form a permutation
  vec<IntVar*> costas;
  createVars(costas, n, 1, n);
  all_different(costas);

  // difference triangle: for each length l, the n-l values X_i - X_{i+l} must be all different
  for (int l = 1; l < n; ++l) {
    vec<IntVar*> line;
    for (int i = 0; i + l < n; ++i) {
      IntVar* d = newIntVar(-(n - 1), n - 1);
      int_minus(costas[i], costas[i + l], d);
      line.push(d);
    }
    all_different(line);
  }

  branch(costas, VAR_INORDER, VAL_MIN);
  json arr = json::array();
  for (int i = 0; i < n; ++i) arr.push_back(dcp::out(costas[i]));
  outputs = {{"costas", arr}};
}
