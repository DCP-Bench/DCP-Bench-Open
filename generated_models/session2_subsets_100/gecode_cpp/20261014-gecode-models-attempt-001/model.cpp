#include "dcp.h"

// Equal-sum split: from a set A of distinct integers, find two disjoint non-empty
// subsets S and T whose elements have the same sum. in_S[i] and in_T[i] say whether
// element i of A belongs to S and to T.
class EqualSumSubsets : public dcp::Space {
 protected:
  BoolVarArray in_S;  // in_S[i] = 1 if A[i] is in S
  BoolVarArray in_T;  // in_T[i] = 1 if A[i] is in T

 public:
  explicit EqualSumSubsets(const json& instance) {
    std::vector<int> A = instance.at("A").get<std::vector<int>>();
    int n = static_cast<int>(A.size());
    in_S = BoolVarArray(*this, n, 0, 1);
    in_T = BoolVarArray(*this, n, 0, 1);

    // S and T are disjoint: no element is in both
    for (int i = 0; i < n; ++i) {
      BoolVarArgs both;
      both << in_S[i] << in_T[i];
      linear(*this, both, IRT_LQ, 1);
    }

    // the sum of the elements in S equals the sum of the elements in T
    IntArgs weight(2 * n);
    BoolVarArgs member(2 * n);
    for (int i = 0; i < n; ++i) {
      weight[i] = A[i];
      weight[n + i] = -A[i];
      member[i] = in_S[i];
      member[n + i] = in_T[i];
    }
    linear(*this, weight, member, IRT_EQ, 0);

    // S is non-empty
    {
      BoolVarArgs s;
      for (int i = 0; i < n; ++i) s << in_S[i];
      linear(*this, s, IRT_GQ, 1);
    }

    // T is non-empty
    {
      BoolVarArgs t;
      for (int i = 0; i < n; ++i) t << in_T[i];
      linear(*this, t, IRT_GQ, 1);
    }

    branch(*this, in_S, BOOL_VAR_NONE(), BOOL_VAL_MIN());
    branch(*this, in_T, BOOL_VAR_NONE(), BOOL_VAL_MIN());

    output("in_S", in_S);
    output("in_T", in_T);
  }

  EqualSumSubsets(EqualSumSubsets& s) : dcp::Space(s) {
    in_S.update(*this, s.in_S);
    in_T.update(*this, s.in_T);
  }
  Gecode::Space* copy() override { return new EqualSumSubsets(*this); }
};

DCP_MODEL(EqualSumSubsets)
