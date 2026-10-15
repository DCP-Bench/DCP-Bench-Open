#include "dcp.h"

// Three sum (subset sum with a fixed size): given n integers, select exactly m of
// them so that the selected numbers sum to zero. Output: indices[i] is true when
// element i is selected.
class ThreeSum : public dcp::Space {
 protected:
  BoolVarArray sel;  // sel[i]: element i is selected

 public:
  explicit ThreeSum(const json& instance) {
    std::vector<int> nums = instance.at("nums").get<std::vector<int>>();
    int m = instance.at("m").get<int>();
    int n = static_cast<int>(nums.size());

    sel = BoolVarArray(*this, n, 0, 1);

    // exactly m elements are selected (the instance's m)
    {
      BoolVarArgs chosen;
      for (int i = 0; i < n; ++i) chosen << sel[i];
      linear(*this, chosen, IRT_EQ, m);
    }

    // the selected numbers sum to zero
    {
      BoolVarArgs chosen;
      for (int i = 0; i < n; ++i) chosen << sel[i];
      linear(*this, IntArgs(nums), chosen, IRT_EQ, 0);
    }

    branch(*this, sel, BOOL_VAR_NONE(), BOOL_VAL_MIN());
    output("indices", sel);
  }

  ThreeSum(ThreeSum& s) : dcp::Space(s) { sel.update(*this, s.sel); }
  Gecode::Space* copy() override { return new ThreeSum(*this); }
};

DCP_MODEL(ThreeSum)
