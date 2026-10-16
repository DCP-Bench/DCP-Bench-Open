#include "dcp.h"

#include <algorithm>

// Car sequencing: order the cars of several types on an assembly line so that
// every option station copes with its share of the cars. Each option o may be
// needed by at most at_most[o] cars in any window of per_slots[o] consecutive
// cars. The output lists the car type of each position, with 0-based types.
//
// Internal values renumber the car types so that value 0 is the most constrained
// type (its options are the tightest), and slots are branched in order with the
// smallest value first. The output maps back to the original type numbers.
class CarSequencing : public dcp::Space {
 protected:
  IntVarArray slot;   // slot[i]: internal type of the car at position i
  IntVarArray type;   // type[i]: original type of the car at position i

 public:
  explicit CarSequencing(const json& instance) {
    std::vector<int> demand = instance.at("demand").get<std::vector<int>>();
    std::vector<int> at_most = instance.at("at_most").get<std::vector<int>>();
    std::vector<int> per_slots = instance.at("per_slots").get<std::vector<int>>();
    std::vector<std::vector<int>> requires = instance.at("requires").get<std::vector<std::vector<int>>>();

    const int classes = static_cast<int>(demand.size());
    const int options = static_cast<int>(at_most.size());
    int cars = 0;
    for (int d : demand) cars += d;

    // hardness of a type: sum over the options it needs of at_most / per_slots
    std::vector<double> hardness(classes, 0.0);
    for (int c = 0; c < classes; ++c)
      for (int o = 0; o < options; ++o)
        if (requires[c][o]) hardness[c] += static_cast<double>(at_most[o]) / per_slots[o];
    std::vector<int> order(classes);
    for (int c = 0; c < classes; ++c) order[c] = c;
    std::stable_sort(order.begin(), order.end(),
                     [&](int a, int b) { return hardness[a] > hardness[b]; });

    // internal value v stands for the original type order[v]
    std::vector<int> order_args(order.begin(), order.end());
    slot = IntVarArray(*this, cars, 0, classes - 1);
    type = IntVarArray(*this, cars, 0, classes - 1);

    // every type appears as often as its demand asks
    for (int v = 0; v < classes; ++v)
      count(*this, slot, v, IRT_EQ, demand[order[v]]);

    // the station for each option: a car needing the option is a 1 in the
    // Boolean row of that option; a window of per_slots cars holds at most at_most ones
    for (int o = 0; o < options; ++o) {
      std::vector<int> needs(classes);
      int total_needing = 0;
      for (int v = 0; v < classes; ++v) {
        needs[v] = requires[order[v]][o];
        total_needing += needs[v] * demand[order[v]];
      }
      const int a = at_most[o];
      const int q = per_slots[o];

      IntVarArgs row;
      for (int i = 0; i < cars; ++i) {
        IntVar b(*this, 0, 1);
        element(*this, IntArgs(needs), slot[i], b);
        row << b;
      }
      // no more than at_most cars needing this option in any window of q
      sequence(*this, row, IntSet(1, 1), q, 0, a, IPL_DOM);

      // implied prefix bounds: the first t cars hold at most
      // a*(t/q)+min(a,t%q) cars needing the option, and at least
      // total_needing minus the same bound for the remaining cars
      IntVarArgs prefix;
      for (int t = 1; t <= cars; ++t) {
        prefix << row[t - 1];
        int upper = a * (t / q) + std::min(a, t % q);
        int rest = cars - t;
        int rest_upper = a * (rest / q) + std::min(a, rest % q);
        int lower = total_needing - rest_upper;
        if (upper < t) linear(*this, prefix, IRT_LQ, upper);
        if (lower > 0) linear(*this, prefix, IRT_GQ, lower);
      }
    }

    // the car type of each position, mapped back to the original numbering
    for (int i = 0; i < cars; ++i) element(*this, IntArgs(order_args), slot[i], type[i]);

    branch(*this, slot, INT_VAR_NONE(), INT_VAL_MIN());
    output("sequence", type);
  }

  CarSequencing(CarSequencing& s) : dcp::Space(s) {
    slot.update(*this, s.slot);
    type.update(*this, s.type);
  }
  Gecode::Space* copy() override { return new CarSequencing(*this); }
};

DCP_MODEL(CarSequencing)
