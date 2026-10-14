#include "dcp.h"

// Four numbers: find three integers x, each between 1 and 10, such that every
// given number can be written as the sum of a non-empty subset of x.
class FourNumbers : public dcp::Space {
 protected:
  IntVarArray x;  // the three integers to find

 public:
  explicit FourNumbers(const json& instance) {
    std::vector<int> numbers = instance.at("numbers").get<std::vector<int>>();

    // the three integers are each between 1 and 10 inclusive
    x = IntVarArray(*this, 3, 1, 10);

    // the seven non-empty subset sums of x
    IntVarArgs sums;
    for (int mask = 1; mask < 8; ++mask) {
      IntVarArgs part;
      for (int k = 0; k < 3; ++k)
        if (mask & (1 << k)) part << x[k];
      sums << expr(*this, sum(part));
    }

    // every given number is one of the subset sums
    for (int r : numbers) {
      IntVar value(*this, r, r);
      member(*this, sums, value, IPL_DOM);
    }

    // search: the three integers, smallest first
    branch(*this, x, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    output("x", x);
  }

  FourNumbers(FourNumbers& s) : dcp::Space(s) { x.update(*this, s.x); }
  Gecode::Space* copy() override { return new FourNumbers(*this); }
};

DCP_MODEL(FourNumbers)
