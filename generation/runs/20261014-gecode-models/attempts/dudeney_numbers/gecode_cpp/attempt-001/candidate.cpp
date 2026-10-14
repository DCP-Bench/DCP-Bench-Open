#include "dcp.h"

// Dudeney numbers: find a perfect cube larger than 1 whose decimal digits sum to
// the cube root of the number. The instance n bounds the number of digits: the
// number is below 10^n (leading zeros are allowed in the digit list).

class Dudeney : public dcp::Space {
 protected:
  IntVar root;                 // cube root of the number
  IntVar number;               // the Dudeney number
  IntVarArray digit;           // decimal digits of number, digit[i] has weight 10^i

 public:
  explicit Dudeney(const json& instance) {
    int n = instance.at("n").get<int>();

    // 10^n, the exclusive upper bound on the number, and the largest root with
    // root^3 < 10^n.
    long long limit = 1;
    for (int i = 0; i < n; ++i) limit *= 10;
    long long top = 1;
    while ((top + 1) * (top + 1) * (top + 1) < limit) ++top;

    // cubes[k] = k^3, so element(cubes, root, number) makes number the cube of root
    std::vector<int> cubes(top + 1);
    for (long long k = 0; k <= top; ++k) cubes[k] = static_cast<int>(k * k * k);

    // the number is a perfect cube larger than 1: root from 2 up to the largest
    // root whose cube is below 10^n
    root = IntVar(*this, 2, static_cast<int>(top));
    number = IntVar(*this, 8, cubes[top]);
    element(*this, IntArgs(cubes), root, number, IPL_DOM);

    // the number is written in n decimal digits
    digit = IntVarArray(*this, n, 0, 9);
    IntVarArgs terms;
    IntArgs weights(n + 1);
    long long weight = 1;
    for (int i = 0; i < n; ++i) {
      terms << digit[i];
      weights[i] = static_cast<int>(weight);
      weight *= 10;
    }
    terms << number;
    weights[n] = -1;
    // the digits, weighted by their place value, add up to the number
    linear(*this, weights, terms, IRT_EQ, 0, IPL_DOM);

    // the digits sum to the cube root
    rel(*this, sum(digit) == root);

    branch(*this, root, INT_VAL_MIN());
    branch(*this, digit, INT_VAR_NONE(), INT_VAL_MIN());
    output("number", number);
  }

  Dudeney(Dudeney& s) : dcp::Space(s) {
    root.update(*this, s.root);
    number.update(*this, s.number);
    digit.update(*this, s.digit);
  }
  Gecode::Space* copy() override { return new Dudeney(*this); }
};

DCP_MODEL(Dudeney)
