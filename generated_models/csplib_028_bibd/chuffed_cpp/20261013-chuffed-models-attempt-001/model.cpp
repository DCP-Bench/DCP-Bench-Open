// Balanced incomplete block design: a v x b binary incidence matrix with r ones per row,
// k ones per column, and a scalar product of l between every pair of distinct rows.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int v = instance.at("v");  // objects (rows of the matrix)
  int b = instance.at("b");  // blocks (columns of the matrix)
  int r = instance.at("r");  // blocks containing each object
  int k = instance.at("k");  // objects in each block
  int l = instance.at("l");  // blocks containing each pair of objects

  // incidence[i][j] = 1 if object i is in block j
  vec<vec<IntVar*>> incidence;
  createVars(incidence, v, b, 0, 1, true);

  // each object occurs in exactly r blocks: every row has r ones
  for (int i = 0; i < v; ++i) {
    vec<IntVar*> row;
    for (int j = 0; j < b; ++j) row.push(incidence[i][j]);
    int_linear(row, IRT_EQ, r);
  }

  // each block contains exactly k objects: every column has k ones
  for (int j = 0; j < b; ++j) {
    vec<IntVar*> col;
    for (int i = 0; i < v; ++i) col.push(incidence[i][j]);
    int_linear(col, IRT_EQ, k);
  }

  // every two distinct objects occur together in exactly l blocks:
  // the scalar product of two rows of the incidence matrix is l
  for (int i = 0; i < v; ++i) {
    for (int h = i + 1; h < v; ++h) {
      // both[j] = 1 if objects i and h are both in block j
      vec<IntVar*> both;
      for (int j = 0; j < b; ++j) {
        IntVar* p = newIntVar(0, 1);
        int_times(incidence[i][j], incidence[h][j], p);
        both.push(p);
      }
      int_linear(both, IRT_EQ, l);
    }
  }

  // search over the matrix row by row
  vec<IntVar*> flat;
  flatten(incidence, flat);
  branch(flat, VAR_INORDER, VAL_MIN);

  json matrix = json::array();
  for (int i = 0; i < v; ++i) {
    json row = json::array();
    for (int j = 0; j < b; ++j) row.push_back(dcp::out(incidence[i][j]));
    matrix.push_back(row);
  }
  outputs = {{"matrix", matrix}};
}
