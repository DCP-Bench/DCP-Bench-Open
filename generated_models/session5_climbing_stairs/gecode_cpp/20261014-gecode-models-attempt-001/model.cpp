#include "dcp.h"

// Climbing stairs: climb a stair of n steps, taking m1 to m2 steps per move.
// steps[i] is the number of steps taken at move i, or 0 once the top is reached.
class ClimbingStairs : public dcp::Space {
 protected:
  IntVarArray steps;  // steps[i]: steps taken at move i (0 after the top is reached)

 public:
  explicit ClimbingStairs(const json& instance) {
    int n = instance.at("n").get<int>();
    int m1 = instance.at("m1").get<int>();
    int m2 = instance.at("m2").get<int>();
    // one slot per move: n moves of one step each is the most that can be needed
    const int moves = n;
    steps = IntVarArray(*this, moves, 0, m2);

    // each move takes m1 to m2 steps, or 0 once the top is reached
    std::vector<int> allowed{0};
    for (int k = std::max(m1, 1); k <= m2; ++k) allowed.push_back(k);
    for (int i = 0; i < moves; ++i) dom(*this, steps[i], IntSet(IntArgs(allowed)));

    // the steps taken over all moves add up to the height of the stair
    IntVarArgs taken;
    for (int i = 0; i < moves; ++i) taken << steps[i];
    linear(*this, taken, IRT_EQ, n);

    // zeros only at the end: once no step is taken, no later move takes any
    for (int i = 0; i + 1 < moves; ++i)
      rel(*this, (steps[i] == 0) >> (steps[i + 1] == 0));

    branch(*this, steps, INT_VAR_NONE(), INT_VAL_MAX());
    output("steps", steps);
  }

  ClimbingStairs(ClimbingStairs& s) : dcp::Space(s) {
    steps.update(*this, s.steps);
  }
  Gecode::Space* copy() override { return new ClimbingStairs(*this); }
};

DCP_MODEL(ClimbingStairs)
