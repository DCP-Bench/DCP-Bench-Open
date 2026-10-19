// Problem session2_subsets_100: from a set A of distinct integers, find two disjoint
// non-empty subsets S and T of A whose sums are equal. S union T need not be all of A.
// Output in_S and in_T: one 0/1 entry per element of A, 1 meaning the element is in the subset.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const std::vector<double> A = instance.at("A").get<std::vector<double>>();
  const int n = static_cast<int>(A.size());

  // in_S[i] = 1 if element i of A is in S; in_T[i] = 1 if element i of A is in T
  std::vector<dcp::Lin> in_S, in_T;
  for (int i = 0; i < n; i++) {
    in_S.push_back(dcp::new_var(h, 0, 1));
    in_T.push_back(dcp::new_var(h, 0, 1));
  }

  // S and T are disjoint: no element is in both
  for (int i = 0; i < n; i++) {
    // element i is in at most one of S and T
    dcp::add_row(h, in_S[i] + in_T[i], -kHighsInf, 1);
  }

  // S is non-empty: at least one element is in S
  dcp::Lin size_S, size_T;
  for (int i = 0; i < n; i++) {
    size_S = size_S + in_S[i];
    size_T = size_T + in_T[i];
  }
  dcp::add_row(h, size_S, 1, kHighsInf);
  // T is non-empty: at least one element is in T
  dcp::add_row(h, size_T, 1, kHighsInf);

  // the sum of the elements in S equals the sum of the elements in T
  dcp::Lin sum_S, sum_T;
  for (int i = 0; i < n; i++) {
    sum_S = sum_S + A[i] * in_S[i];
    sum_T = sum_T + A[i] * in_T[i];
  }
  dcp::add_row(h, sum_S - sum_T, 0, 0);

  out.add("in_S", in_S);
  out.add("in_T", in_T);
}
