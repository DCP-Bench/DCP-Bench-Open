#include "dcp.h"

// Among: choose the values of x (an array of n integers, each in 0..7) so that
// exactly m of them take one of the values in v.
class Among : public dcp::Space {
 protected:
  IntVarArray x;  // x[i]: the i-th value, in 0..7 (the description's bounds)

 public:
  explicit Among(const json& instance) {
    int n = instance.at("n").get<int>();
    int m = instance.at("m").get<int>();
    std::vector<int> v = instance.at("v").get<std::vector<int>>();

    // the description fixes every value of x to lie in 0..7
    x = IntVarArray(*this, n, 0, 7);

    // exactly m entries of x take one of the values in v
    count(*this, x, IntSet(IntArgs(v)), IRT_EQ, m, IPL_DOM);

    branch(*this, x, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    output("x", x);
  }

  Among(Among& s) : dcp::Space(s) { x.update(*this, s.x); }
  Gecode::Space* copy() override { return new Among(*this); }
};

DCP_MODEL(Among)
