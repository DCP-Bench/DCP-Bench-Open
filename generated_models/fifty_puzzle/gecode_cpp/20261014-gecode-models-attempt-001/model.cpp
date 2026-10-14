#include "dcp.h"

// Fifty puzzle (side show): knock over a selection of dummies with baseballs so that
// the numbers on the dummies knocked over add up to exactly the target sum. Print
// which dummies are knocked over.
class FiftyPuzzle : public dcp::Space {
 protected:
  BoolVarArray dummies;  // dummies[i] = 1 if dummy i is knocked over

 public:
  explicit FiftyPuzzle(const json& instance) {
    int target = instance.at("target_sum").get<int>();
    std::vector<int> values = instance.at("values").get<std::vector<int>>();
    int n = static_cast<int>(values.size());

    // one Boolean per dummy: knocked over or not
    dummies = BoolVarArray(*this, n, 0, 1);

    // the numbers on the dummies knocked over sum to exactly the target, neither more nor less
    linear(*this, IntArgs(values), BoolVarArgs(dummies), IRT_EQ, target, IPL_DOM);

    // decide each dummy in turn, trying "not knocked over" first
    branch(*this, dummies, BOOL_VAR_NONE(), BOOL_VAL_MIN());

    output("dummies", dummies);
  }

  FiftyPuzzle(FiftyPuzzle& s) : dcp::Space(s) { dummies.update(*this, s.dummies); }
  Gecode::Space* copy() override { return new FiftyPuzzle(*this); }
};

DCP_MODEL(FiftyPuzzle)
