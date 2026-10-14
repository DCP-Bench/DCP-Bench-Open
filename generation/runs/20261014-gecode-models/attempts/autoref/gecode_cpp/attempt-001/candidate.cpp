#include "dcp.h"

// Autoreference series: find a series S = (s0, s1, ..., sn, sn+1) such that
// s_i is the number of occurrences of i in S for every i from 0 to n, and the
// last term s_{n+1} equals m. Every term is one of the counted values 0..n.
class Autoref : public dcp::Space {
 protected:
  IntVarArray s;  // s[j]: the j-th term of the series, j = 0..n+1

 public:
  explicit Autoref(const json& instance) {
    int n = instance.at("n").get<int>();
    int m = instance.at("m").get<int>();

    // the series has n+2 terms, each one of the values 0..n
    s = IntVarArray(*this, n + 2, 0, n);

    // the last term is m
    rel(*this, s[n + 1] == m);

    // s_i is the number of occurrences of i in the series, for i = 0..n
    for (int i = 0; i <= n; ++i) count(*this, s, i, IRT_EQ, s[i], IPL_DOM);

    // redundant: the counts of the values 0..n add up to the n+2 terms
    IntVarArgs counts;
    for (int i = 0; i <= n; ++i) counts << s[i];
    linear(*this, counts, IRT_EQ, n + 2);

    branch(*this, s, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    output("s", s);
  }

  Autoref(Autoref& sp) : dcp::Space(sp) {
    s.update(*this, sp.s);
  }
  Gecode::Space* copy() override { return new Autoref(*this); }
};

DCP_MODEL(Autoref)
