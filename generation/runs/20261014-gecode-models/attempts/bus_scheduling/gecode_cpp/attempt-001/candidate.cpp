#include "dcp.h"

// Bus scheduling: Progress City needs the fewest buses so that, in each of the
// six 4-hour slots of the day, the buses on duty meet the demand. Each bus works
// 8 successive hours, that is two slots. x[i] is the number of buses that start
// in slot i. The day repeats, so slot 5 is followed by slot 0.
class BusScheduling : public dcp::Space {
 protected:
  IntVarArray x;     // x[i]: buses starting in slot i
  IntVar total;      // total number of buses

 public:
  explicit BusScheduling(const json& instance) {
    std::vector<int> demands = instance.at("demands");
    int n = demands.size();

    // largest demand of any slot
    int maxDemand = 0;
    for (int d : demands) maxDemand = std::max(maxDemand, d);

    // derived bound (not from the instance field itself): in an optimal schedule
    // no x[i] exceeds the largest demand, since at maxDemand the buses starting in
    // slot i already meet the demand of slots i and i+1 on their own
    x = IntVarArray(*this, n, 0, maxDemand);

    for (int i = 0; i < n; ++i) {
      // the buses on duty in slot i are those that started in slot i and in the
      // slot before it, which wraps around for slot 0
      int prev = (i + n - 1) % n;
      IntVarArgs onDuty;
      onDuty << x[prev] << x[i];
      linear(*this, onDuty, IRT_GQ, demands[i], IPL_BND);
    }

    // minimise the total number of buses
    total = expr(*this, sum(x));
    minimize(total);

    branch(*this, x, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    output("x", x);
  }

  BusScheduling(BusScheduling& s) : dcp::Space(s) {
    x.update(*this, s.x);
    total.update(*this, s.total);
  }
  Gecode::Space* copy() override { return new BusScheduling(*this); }
};

DCP_MODEL(BusScheduling)
