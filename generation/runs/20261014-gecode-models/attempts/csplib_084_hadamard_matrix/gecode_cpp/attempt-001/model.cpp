#include "dcp.h"

// Hadamard matrix Legendre pairs of odd length l: two sequences a and b of l
// values in {-1, +1} such that the periodic autocorrelations of a and b sum to
// -2 at every shift s = 1..m (m = (l-1)/2), with sum(a) = 1 and sum(b) = 1.
class HadamardLegendrePairs : public dcp::Space {
 protected:
  int l;               // sequence length, odd (from the instance)
  IntVarArray a;       // a[i]: i-th value of sequence A, in {-1, +1}
  IntVarArray b;       // b[i]: i-th value of sequence B, in {-1, +1}

 public:
  explicit HadamardLegendrePairs(const json& instance)
      : l(instance.at("l").get<int>()) {
    const int m = (l - 1) / 2;

    // every entry of A and B is -1 or +1
    a = IntVarArray(*this, l, -1, 1);
    b = IntVarArray(*this, l, -1, 1);
    dom(*this, a, IntSet(IntArgs({-1, 1})));
    dom(*this, b, IntSet(IntArgs({-1, 1})));

    // for every shift s, PAF(A, s) + PAF(B, s) = -2, where
    // PAF(X, s) = sum_i x_i * x_{(i+s) mod l} is the periodic autocorrelation.
    // Each product is a {-1, +1} variable, so the sum of the 2l products is -2.
    for (int s = 1; s <= m; ++s) {
      IntVarArgs products;
      for (int i = 0; i < l; ++i) {
        // the i-th term of PAF(A, s)
        IntVar pa(*this, -1, 1);
        dom(*this, pa, IntSet(IntArgs({-1, 1})));
        mult(*this, a[i], a[(i + s) % l], pa, IPL_DOM);
        products << pa;
        // the i-th term of PAF(B, s)
        IntVar pb(*this, -1, 1);
        dom(*this, pb, IntSet(IntArgs({-1, 1})));
        mult(*this, b[i], b[(i + s) % l], pb, IPL_DOM);
        products << pb;
      }
      // PAF(A, s) + PAF(B, s) = -2
      linear(*this, products, IRT_EQ, -2, IPL_BND);
    }

    // the entries of A sum to 1
    linear(*this, a, IRT_EQ, 1, IPL_BND);
    // the entries of B sum to 1
    linear(*this, b, IRT_EQ, 1, IPL_BND);

    branch(*this, a, INT_VAR_NONE(), INT_VAL_MIN());
    branch(*this, b, INT_VAR_NONE(), INT_VAL_MIN());

    output("a", a);
    output("b", b);
  }

  HadamardLegendrePairs(HadamardLegendrePairs& s) : dcp::Space(s), l(s.l) {
    a.update(*this, s.a);
    b.update(*this, s.b);
  }

  Gecode::Space* copy() override { return new HadamardLegendrePairs(*this); }
};

DCP_MODEL(HadamardLegendrePairs)
