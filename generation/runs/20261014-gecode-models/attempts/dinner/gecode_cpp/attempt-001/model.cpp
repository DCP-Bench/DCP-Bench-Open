#include "dcp.h"

// Dinner party: choose how many grandparents, parents and children go out to
// dinner. 1-6 grandparents, 1-10 parents, 1-40 children. Exactly 20 people in
// total, and the bill is exactly $20: grandparents $3, parents $2, children $0.50.
// The instance has no data fields; every number comes from the description.
class Dinner : public dcp::Space {
 protected:
  IntVar grandparents;  // number of grandparents going to dinner
  IntVar parents;       // number of parents going to dinner
  IntVar children;      // number of children going to dinner

 public:
  explicit Dinner(const json& instance) {
    (void)instance;

    // 1-6 grandparents, 1-10 parents and/or 1-40 children
    grandparents = IntVar(*this, 1, 6);
    parents = IntVar(*this, 1, 10);
    children = IntVar(*this, 1, 40);

    IntVarArgs people;
    people << grandparents << parents << children;

    // there must be 20 total people at dinner
    linear(*this, IntArgs({1, 1, 1}), people, IRT_EQ, 20, IPL_DOM);

    // it must cost $20: grandparents $3, parents $2, children $0.50.
    // Costs are doubled so every coefficient is an integer:
    // 6 * grandparents + 4 * parents + 1 * children = 2 * 20 = 40
    linear(*this, IntArgs({6, 4, 1}), people, IRT_EQ, 40, IPL_DOM);

    // the question asks for the counts only, so there is no objective;
    // branch on the three counts (domains are small)
    branch(*this, people, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    output("grandparents", grandparents);
    output("parents", parents);
    output("children", children);
  }

  Dinner(Dinner& s) : dcp::Space(s) {
    grandparents.update(*this, s.grandparents);
    parents.update(*this, s.parents);
    children.update(*this, s.children);
  }
  Gecode::Space* copy() override { return new Dinner(*this); }
};

DCP_MODEL(Dinner)
