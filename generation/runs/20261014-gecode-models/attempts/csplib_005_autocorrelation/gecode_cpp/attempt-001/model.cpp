#include "dcp.h"

// Binary sequence of length n with entries +1 or -1 that minimises the energy,
// the sum over k = 1..n-1 of the squared periodic autocorrelations C_k.
class Autocorrelation : public dcp::Space {
 protected:
  IntVarArray bit;  // bit[i] = 1 when the i-th entry is +1, 0 when it is -1
  IntVarArray seq;  // seq[i] = +1 or -1, the printed sequence
  IntVar energy;    // sum of C_k^2 over k = 1..n-1

 public:
  explicit Autocorrelation(const json& instance) {
    int n = instance.at("n").get<int>();
    bit = IntVarArray(*this, n, 0, 1);
    seq = IntVarArray(*this, n, -1, 1);

    // each entry is +1 or -1: seq[i] = 2 * bit[i] - 1
    for (int i = 0; i < n; ++i) {
      IntVarArgs x;
      x << seq[i] << bit[i];
      linear(*this, IntArgs({1, -2}), x, IRT_EQ, -1);
    }

    // periodic k-th autocorrelation C_k = sum_i seq[i] * seq[(i+k) mod n]
    // A product of two entries is -1 when the bits differ and +1 when they agree,
    // so C_k = n - 2 * (number of i where bit[i] and bit[(i+k) mod n] differ).
    IntVarArgs squares;
    for (int k = 1; k < n; ++k) {
      BoolVarArgs differ;
      for (int i = 0; i < n; ++i) {
        BoolVar d(*this, 0, 1);
        rel(*this, bit[i], IRT_NQ, bit[(i + k) % n], d);
        differ << d;
      }
      // D = number of differing pairs at shift k
      IntVar D(*this, 0, n);
      linear(*this, differ, IRT_EQ, D);

      // C_k = n - 2 D, so C_k + 2 D = n
      IntVar ck(*this, -n, n);
      IntVarArgs x;
      x << ck << D;
      linear(*this, IntArgs({1, 2}), x, IRT_EQ, n);

      // squared autocorrelation C_k^2, one term of the energy
      IntVar sq(*this, 0, n * n);
      sqr(*this, ck, sq, IPL_DOM);
      squares << sq;
    }

    // energy E = sum over k of C_k^2, to be minimised
    energy = expr(*this, sum(squares));

    // the bits decide everything else, so branch on them
    branch(*this, bit, INT_VAR_NONE(), INT_VAL_MIN());
    minimize(energy);
    output("sequence", seq);
  }

  Autocorrelation(Autocorrelation& s) : dcp::Space(s) {
    bit.update(*this, s.bit);
    seq.update(*this, s.seq);
    energy.update(*this, s.energy);
  }
  Gecode::Space* copy() override { return new Autocorrelation(*this); }
};

DCP_MODEL(Autocorrelation)
