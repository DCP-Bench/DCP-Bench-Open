// Number partitioning: split the numbers 1..N into two sets A and B of equal size, equal sums and equal sums of squares.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("n");

  // in_a[i] = 1 if the number i+1 is in set A, 0 if it is in set B
  vec<IntVar*> in_a;
  createVars(in_a, n, 0, 1, true);
  // in_b[i] = 1 - in_a[i]: the number i+1 is in set B
  vec<IntVar*> in_b;
  createVars(in_b, n, 0, 1, true);
  for (int i = 0; i < n; ++i) {
    vec<int> flip_coef;
    flip_coef.push(1);
    flip_coef.push(1);
    vec<IntVar*> pair;
    pair.push(in_a[i]);
    pair.push(in_b[i]);
    int_linear(flip_coef, pair, IRT_EQ, 1);
  }

  // A and B have the same cardinality: 2 * |A| = N
  vec<int> ones_a;
  for (int i = 0; i < n; ++i) ones_a.push(2);
  int_linear(ones_a, in_a, IRT_EQ, n);

  // the sums are equal: 2 * sum(A) = N(N+1)/2, written without division
  int total = n * (n + 1) / 2;
  vec<int> sum_coef;
  for (int i = 0; i < n; ++i) sum_coef.push(2 * (i + 1));
  int_linear(sum_coef, in_a, IRT_EQ, total);

  // the sums of squares are equal: 2 * sum of squares of A = sum of squares of 1..N
  int total_sq = n * (n + 1) * (2 * n + 1) / 6;
  vec<int> sq_coef;
  for (int i = 0; i < n; ++i) sq_coef.push(2 * (i + 1) * (i + 1));
  int_linear(sq_coef, in_a, IRT_EQ, total_sq);

  // the sets are output as sorted lists: a[k] is the k-th smallest number of A, and it must be in A
  int half = n / 2;
  vec<IntVar*> a_list;
  createVars(a_list, half, 1, n);
  for (int k = 0; k < half; ++k) {
    // a[k] must be a number whose indicator in A is 1 (indexed from 1)
    array_var_int_element_bound(a_list[k], in_a, getConstant(1), 1);
    if (k + 1 < half) {
      // the numbers of A are listed in increasing order
      int_rel(a_list[k], IRT_LT, a_list[k + 1]);
    }
  }

  // b[k] is the k-th smallest number of B, and it must be in B
  vec<IntVar*> b_list;
  createVars(b_list, half, 1, n);
  for (int k = 0; k < half; ++k) {
    // b[k] must be a number whose indicator in B is 1 (indexed from 1)
    array_var_int_element_bound(b_list[k], in_b, getConstant(1), 1);
    if (k + 1 < half) {
      // the numbers of B are listed in increasing order
      int_rel(b_list[k], IRT_LT, b_list[k + 1]);
    }
  }

  // search on the membership of each number in A
  branch(in_a, VAR_INORDER, VAL_MIN);

  json set_a = json::array();
  for (int k = 0; k < half; ++k) set_a.push_back(dcp::out(a_list[k]));
  json set_b = json::array();
  for (int k = 0; k < half; ++k) set_b.push_back(dcp::out(b_list[k]));
  outputs = {{"A", set_a}, {"B", set_b}};
}
