#include "dcp.h"

#include <algorithm>

// Car sequencing: order the cars of several types on an assembly line so that
// every option station copes with its share of the cars. Option o may be needed
// by at most at_most[o] cars in any window of per_slots[o] consecutive cars.
// The output lists the car type at each position, with 0-based types.
//
// Internally the types are renumbered: value 0 is the type that needs the most
// heavily used options (utilisation order, ties lexicographic). Slots are branched
// in order with the smallest value first.
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

    // utilisation of an option: share of cars needing it relative to its capacity
    std::vector<double> util(options, 0.0);
    for (int o = 0; o < options; ++o) {
      int need = 0;
      for (int c = 0; c < classes; ++c) need += requires[c][o] * demand[c];
      util[o] = static_cast<double>(need) * per_slots[o] / (static_cast<double>(at_most[o]) * cars);
    }
    std::vector<int> oorder(options);
    for (int o = 0; o < options; ++o) oorder[o] = o;
    std::stable_sort(oorder.begin(), oorder.end(), [&](int a, int b) { return util[a] > util[b]; });
    std::vector<int> order(classes);
    for (int c = 0; c < classes; ++c) order[c] = c;
    std::stable_sort(order.begin(), order.end(), [&](int a, int b) {
      for (int o : oorder)
        if (requires[a][o] != requires[b][o]) return requires[a][o] > requires[b][o];
      return false;
    });

    std::vector<int> order_args(order.begin(), order.end());
    slot = IntVarArray(*this, cars, 0, classes - 1);
    type = IntVarArray(*this, cars, 0, classes - 1);

    // every type appears as often as its demand asks
    IntArgs cards_vals(classes);
    IntVarArgs cards;
    for (int v = 0; v < classes; ++v) {
      cards_vals[v] = v;
      cards << IntVar(*this, demand[order[v]], demand[order[v]]);
    }
    count(*this, slot, cards, cards_vals, IPL_DOM);

    // a car of a type has exactly the options that type requires
    TupleSet table(options + 1);
    for (int v = 0; v < classes; ++v) {
      IntArgs t(options + 1);
      t[0] = v;
      for (int o = 0; o < options; ++o) t[o + 1] = requires[order[v]][o];
      table.add(t);
    }
    table.finalize();
    std::vector<IntVarArgs> need(options);
    for (int i = 0; i < cars; ++i) {
      IntVarArgs row;
      row << slot[i];
      for (int o = 0; o < options; ++o) {
        IntVar b(*this, 0, 1);
        need[o] << b;
        row << b;
      }
      extensional(*this, row, table);
    }

    for (int o = 0; o < options; ++o) {
      int total_needing = 0;
      for (int c = 0; c < classes; ++c) total_needing += requires[c][o] * demand[c];
      const int a = at_most[o];
      const int q = per_slots[o];

      // no more than at_most cars needing this option in any window of per_slots cars
      sequence(*this, need[o], IntSet(1, 1), q, 0, a, IPL_DOM);

      // implied prefix bounds on the cars needing the option
      IntVarArgs prefix;
      for (int t = 1; t <= cars; ++t) {
        prefix << need[o][t - 1];
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
