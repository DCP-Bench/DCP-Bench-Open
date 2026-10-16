#include "dcp.h"

// Magic sequence of length n: x_0, ..., x_{n-1} with values between 0 and n-1,
// such that for every i in 0..n-1 the number i occurs exactly x_i times in the sequence.
class MagicSequence : public dcp::Space {
 protected:
  IntVarArray x;

 public:
  explicit MagicSequence(const json& instance) {
    int n = instance.at("n").get<int>();
    x = IntVarArray(*this, n, 0, n - 1);

    // for every i, the number i occurs exactly x_i times in the sequence
    IntArgs values(n);
    for (int i = 0; i < n; ++i) values[i] = i;
    IntVarArgs counts;
    for (int i = 0; i < n; ++i) counts << x[i];
    count(*this, x, counts, values);

    // the counts add up to the length of the sequence (implied, redundant)
    linear(*this, x, IRT_EQ, n);

    branch(*this, x, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    output("x", x);
  }

  MagicSequence(MagicSequence& s) : dcp::Space(s) { x.update(*this, s.x); }
  Gecode::Space* copy() override { return new MagicSequence(*this); }
};

DCP_MODEL(MagicSequence)
