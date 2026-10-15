#include "dcp.h"

// Joe's account number: a permutation x of the digits 0..n-1 such that, for each
// set of digits, exactly num_correct_digits positions hold the same digit as x.
class JustForgotten : public dcp::Space {
 protected:
  IntVarArray x;  // x[i]: the digit at position i of the account number

 public:
  explicit JustForgotten(const json& instance) {
    const std::vector<std::vector<int>> sets =
        instance.at("sets").get<std::vector<std::vector<int>>>();
    const int k = instance.at("num_correct_digits").get<int>();
    const int n = static_cast<int>(sets[0].size());  // digits 0..n-1, n taken from the sets
    x = IntVarArray(*this, n, 0, n - 1);

    // the account number has all the digits from 0 to n-1 in some order
    distinct(*this, x, IPL_DOM);

    // in each set just k digits are in their correct position
    for (const auto& set : sets) {
      BoolVarArgs same;
      for (int i = 0; i < n; ++i)
        same << expr(*this, x[i] == set[i]);
      linear(*this, same, IRT_EQ, k);
    }

    branch(*this, x, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    output("x", x);
  }

  JustForgotten(JustForgotten& s) : dcp::Space(s) {
    x.update(*this, s.x);
  }
  Gecode::Space* copy() override { return new JustForgotten(*this); }
};

DCP_MODEL(JustForgotten)
