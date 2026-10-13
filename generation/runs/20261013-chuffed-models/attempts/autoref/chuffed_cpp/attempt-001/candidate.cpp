// Autoreferential sequence: find S = (s0, ..., sn, sn+1) where s_i is the number of occurrences of i in S for i = 0..n, and s_{n+1} = m.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("n");
  int m = instance.at("m");
  int len = n + 2;  // the series has n+2 terms: s0 .. sn+1

  // s[j] is the j-th term of the series; the terms are counts of the values 0..n, so each term lies in 0..n
  vec<IntVar*> s;
  createVars(s, len, 0, n, true);

  // the last term is the given value m
  int_rel(s[n + 1], IRT_EQ, m);

  // for each i from 0 to n, the number of terms equal to i must be s_i
  for (int i = 0; i <= n; ++i) {
    // occ[j] = 1 if term j equals i
    vec<BoolView> occ;
    for (int j = 0; j < len; ++j) {
      BoolView b = newBoolVar();
      int_rel_reif(s[j], IRT_EQ, i, b);
      occ.push(b);
    }
    // the count of true entries in occ is the value of term i
    bool_linear(occ, IRT_EQ, s[i]);
  }

  // the terms s0 .. sn are the decision variables
  vec<IntVar*> decision;
  for (int i = 0; i <= n; ++i) decision.push(s[i]);
  branch(decision, VAR_INORDER, VAL_MIN);

  json arr = json::array();
  for (int j = 0; j < len; ++j) arr.push_back(dcp::out(s[j]));
  outputs = {{"s", arr}};
}
