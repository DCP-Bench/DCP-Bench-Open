// Equal-sum subsets: find two disjoint non-empty subsets S and T of A whose elements have the same sum.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<int> A = instance.at("A").get<std::vector<int>>();
  int n = static_cast<int>(A.size());

  // in_S[i] = 1 if A[i] is in S; in_T[i] = 1 if A[i] is in T
  vec<IntVar*> in_S, in_T;
  createVars(in_S, n, 0, 1, true);
  createVars(in_T, n, 0, 1, true);

  // S and T are disjoint: no element is in both
  for (int i = 0; i < n; ++i) {
    vec<IntVar*> both;
    both.push(in_S[i]);
    both.push(in_T[i]);
    int_linear(both, IRT_LE, 1);
  }

  // S and T are both non-empty
  int_linear(in_S, IRT_GE, 1);
  int_linear(in_T, IRT_GE, 1);

  // the sum of the elements of S equals the sum of the elements of T
  vec<int> coef;
  vec<IntVar*> vars;
  for (int i = 0; i < n; ++i) {
    coef.push(A[i]);
    vars.push(in_S[i]);
  }
  for (int i = 0; i < n; ++i) {
    coef.push(-A[i]);
    vars.push(in_T[i]);
  }
  int_linear(coef, vars, IRT_EQ, 0);

  vec<IntVar*> all;
  for (int i = 0; i < n; ++i) all.push(in_S[i]);
  for (int i = 0; i < n; ++i) all.push(in_T[i]);
  branch(all, VAR_INORDER, VAL_MIN);

  json s_arr = json::array();
  json t_arr = json::array();
  for (int i = 0; i < n; ++i) {
    s_arr.push_back(dcp::out(in_S[i]));
    t_arr.push_back(dcp::out(in_T[i]));
  }
  outputs = {{"in_S", s_arr}, {"in_T", t_arr}};
}
