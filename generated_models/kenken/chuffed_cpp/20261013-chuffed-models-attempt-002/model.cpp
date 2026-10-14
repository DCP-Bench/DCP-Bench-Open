// KenKen: fill an n x n grid with the digits 1..n so that every row and every column holds each digit once,
// and every cage has its target under one of the arithmetic operations (+, -, x, /). The operation of each
// cage is not given, so each cage may use any operation that fits its target.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("n");
  const json& cages = instance.at("problem");

  // grid[r][c] = digit in row r, column c
  vec<vec<IntVar*>> grid;
  createVars(grid, n, n, 1, n, true);

  // every row contains each digit once
  for (int r = 0; r < n; ++r) {
    vec<IntVar*> row;
    for (int c = 0; c < n; ++c) row.push(grid[r][c]);
    all_different(row);
  }

  // every column contains each digit once
  for (int c = 0; c < n; ++c) {
    vec<IntVar*> col;
    for (int r = 0; r < n; ++r) col.push(grid[r][c]);
    all_different(col);
  }

  // each cage: [target, cells], with cells given as 1-based [row, column]
  for (const auto& cage : cages) {
    int target = cage[0];
    const auto& cells = cage[1];
    int k = static_cast<int>(cells.size());

    // the digits of the cage, in the order given
    vec<IntVar*> v;
    for (const auto& cell : cells) v.push(grid[cell[0].get<int>() - 1][cell[1].get<int>() - 1]);

    if (k == 1) {
      // a single cell holds the target
      int_rel(v[0], IRT_EQ, target);
      continue;
    }

    // the cage holds if one of its operations gives the target: options[] are the Boolean choices
    vec<BoolView> options;

    // sum of the digits equals the target
    {
      BoolView b = newBoolVar();
      vec<int> ones;
      for (int i = 0; i < k; ++i) ones.push(1);
      int_linear(ones, v, IRT_EQ, target, b);
      options.push(b);
    }

    // product of the digits equals the target (a chain of products through intermediate variables)
    {
      IntVar* p = v[0];
      long long hi = n;
      for (int i = 1; i < k; ++i) {
        hi *= n;
        IntVar* q = newIntVar(1, static_cast<int>(hi));
        int_times(p, v[i], q);
        p = q;
      }
      BoolView b = newBoolVar();
      int_rel_reif(p, IRT_EQ, target, b);
      options.push(b);
    }

    if (k == 2) {
      // difference of the two digits (in either order) equals the target
      IntVar* d = newIntVar(-(n - 1), n - 1);
      int_minus(v[0], v[1], d);
      IntVar* ad = newIntVar(0, n - 1);
      int_abs(d, ad);
      BoolView bd = newBoolVar();
      int_rel_reif(ad, IRT_EQ, target, bd);
      options.push(bd);

      // quotient of the two digits (in either order) equals the target: first = target * second
      vec<int> ratio;
      ratio.push(1);
      ratio.push(-target);
      vec<IntVar*> first_over_second;
      first_over_second.push(v[0]);
      first_over_second.push(v[1]);
      BoolView bq1 = newBoolVar();
      int_linear(ratio, first_over_second, IRT_EQ, 0, bq1);
      options.push(bq1);

      vec<IntVar*> second_over_first;
      second_over_first.push(v[1]);
      second_over_first.push(v[0]);
      BoolView bq2 = newBoolVar();
      int_linear(ratio, second_over_first, IRT_EQ, 0, bq2);
      options.push(bq2);
    }

    bool_clause(options);
  }

  vec<IntVar*> flat;
  flatten(grid, flat);
  branch(flat, VAR_INORDER, VAL_MIN);

  json rows = json::array();
  for (int r = 0; r < n; ++r) {
    json row = json::array();
    for (int c = 0; c < n; ++c) row.push_back(dcp::out(grid[r][c]));
    rows.push_back(row);
  }
  outputs = {{"x", rows}};
}
