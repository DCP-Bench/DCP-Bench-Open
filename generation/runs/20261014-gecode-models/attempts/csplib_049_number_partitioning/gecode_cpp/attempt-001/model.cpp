#include "dcp.h"

// Number partitioning: split the numbers 1..N into two sets A and B such that
// A and B have the same cardinality, the same sum, and the same sum of squares.
//
// Encoding: x holds the numbers 1..N in one permutation. The first N/2 entries
// are the set A and the rest are the set B, each listed in increasing order.
class NumberPartitioning : public dcp::Space {
 protected:
  int n;           // N, the largest number to partition (from the instance)
  IntVarArray x;   // x[0..k-1] = A, x[k..n-1] = B, k = N/2
  IntVarArray sq;  // sq[i] = x[i]^2

 public:
  explicit NumberPartitioning(const json& instance) {
    n = instance.at("n").get<int>();
    if (n % 2 != 0) throw std::invalid_argument("N must be even for two sets of equal size");
    int k = n / 2;

    x = IntVarArray(*this, n, 1, n);
    sq = IntVarArray(*this, n, 1, n * n);

    // every number 1..N is in exactly one of the two sets
    distinct(*this, x, IPL_DOM);

    // the two sets are interchangeable, so fix that 1 is in A
    rel(*this, x[0], IRT_EQ, 1);

    // each set is listed in increasing order
    for (int i = 0; i + 1 < k; ++i) rel(*this, x[i], IRT_LE, x[i + 1]);
    for (int i = k; i + 1 < n; ++i) rel(*this, x[i], IRT_LE, x[i + 1]);

    // sum of numbers in A = sum of numbers in B
    IntArgs sign(n);
    for (int i = 0; i < n; ++i) sign[i] = i < k ? 1 : -1;
    linear(*this, sign, x, IRT_EQ, 0);

    // sum of squares of numbers in A = sum of squares of numbers in B
    for (int i = 0; i < n; ++i) rel(*this, x[i] * x[i] == sq[i]);
    linear(*this, sign, sq, IRT_EQ, 0);

    branch(*this, x, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    branch(*this, sq, INT_VAR_NONE(), INT_VAL_MIN());

    // the printed sets: A and B
    IntVarArgs A, B;
    for (int i = 0; i < k; ++i) A << x[i];
    for (int i = k; i < n; ++i) B << x[i];
    output("A", A);
    output("B", B);
  }

  NumberPartitioning(NumberPartitioning& s) : dcp::Space(s), n(s.n) {
    x.update(*this, s.x);
    sq.update(*this, s.sq);
  }
  Gecode::Space* copy() override { return new NumberPartitioning(*this); }
};

DCP_MODEL(NumberPartitioning)
