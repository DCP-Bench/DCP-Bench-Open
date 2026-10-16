#include "dcp.h"

// All-interval series of size n: a permutation x of 0..n-1 whose neighbouring
// differences |x[i+1] - x[i]| form a permutation diffs of 1..n-1.
class AllInterval : public dcp::Space {
 protected:
  IntVarArray x;      // the series: x[i] is the pitch class at position i
  IntVarArray diffs;  // diffs[i]: interval between neighbouring notes i and i+1

 public:
  explicit AllInterval(const json& instance) {
    int n = instance.at("n").get<int>();
    x = IntVarArray(*this, n, 0, n - 1);
    diffs = IntVarArray(*this, n - 1, 1, n - 1);

    // each pitch class occurs exactly once in the series
    distinct(*this, x, IPL_DOM);

    // the intervals between neighbouring notes are all different,
    // so together they cover every interval from 1 to n-1
    distinct(*this, diffs, IPL_DOM);

    // diffs[i] is the interval between neighbouring notes x[i] and x[i+1]
    for (int i = 0; i + 1 < n; ++i)
      abs(*this, expr(*this, x[i + 1] - x[i]), diffs[i], IPL_DOM);

    // symmetry breaking: reversing a series gives another series, so fix the
    // order of its first and last pitch classes
    rel(*this, x[0] < x[n - 1]);

    restarts(100);
    branch(*this, x, INT_VAR_AFC_SIZE_MAX(0.99), INT_VAL_MIN());
    branch(*this, diffs, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    output("x", x);
    output("diffs", diffs);
  }

  AllInterval(AllInterval& s) : dcp::Space(s) {
    x.update(*this, s.x);
    diffs.update(*this, s.diffs);
  }
  Gecode::Space* copy() override { return new AllInterval(*this); }
};

DCP_MODEL(AllInterval)
