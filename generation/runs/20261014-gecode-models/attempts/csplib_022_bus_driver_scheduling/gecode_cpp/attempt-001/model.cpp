#include "dcp.h"

// Bus driver scheduling (CSPLib prob022): choose a set of shifts so that every
// piece of work is covered exactly once, minimising the number of shifts used.
class BusDriverScheduling : public dcp::Space {
 protected:
  BoolVarArray x;   // x[s] = 1 if shift s is selected
  IntVar total;     // number of selected shifts

 public:
  explicit BusDriverScheduling(const json& instance) {
    int num_work = instance.at("num_work").get<int>();
    int num_shifts = instance.at("num_shifts").get<int>();
    const json& shifts = instance.at("shifts");

    // one Boolean per possible shift: selected or not
    x = BoolVarArray(*this, num_shifts, 0, 1);

    // the shifts that cover each piece of work
    std::vector<BoolVarArgs> covering(num_work);
    for (int s = 0; s < num_shifts; ++s)
      for (const auto& w : shifts[s]) covering[w.get<int>()] << x[s];

    // each piece of work is covered by exactly one selected shift
    for (int w = 0; w < num_work; ++w) linear(*this, covering[w], IRT_EQ, 1);

    // the number of selected shifts, which is the cost (every shift costs the same)
    total = expr(*this, sum(x));

    // branch on the shifts: selecting one removes the shifts that overlap it
    branch(*this, x, BOOL_VAR_AFC_MAX(0.99), BOOL_VAL_MAX());
    restarts(100);
    minimize(total);
    output("x", x);
  }

  BusDriverScheduling(BusDriverScheduling& s) : dcp::Space(s) {
    x.update(*this, s.x);
    total.update(*this, s.total);
  }
  Gecode::Space* copy() override { return new BusDriverScheduling(*this); }
};

DCP_MODEL(BusDriverScheduling)
