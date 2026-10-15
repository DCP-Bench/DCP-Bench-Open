#include "dcp.h"

// Car sequencing: order the cars on an assembly line so that every car type is
// built as often as its demand and no option station gets more cars than it can
// handle in any window of consecutive cars.
class CarSequencing : public dcp::Space {
 protected:
  IntVarArray seq;  // seq[p]: car type at position p of the line

 public:
  explicit CarSequencing(const json& instance) {
    std::vector<int> demand = instance.at("demand").get<std::vector<int>>();
    std::vector<int> at_most = instance.at("at_most").get<std::vector<int>>();
    std::vector<int> per_slots = instance.at("per_slots").get<std::vector<int>>();
    const json& requires_option = instance.at("requires");  // requires[type][option]

    int types = static_cast<int>(demand.size());
    int options = static_cast<int>(at_most.size());
    int cars = 0;
    for (int d : demand) cars += d;

    seq = IntVarArray(*this, cars, 0, types - 1);

    // each car type appears as many times as its demand
    for (int t = 0; t < types; ++t) count(*this, seq, t, IRT_EQ, demand[t]);

    // for each option, in any window of per_slots cars at most at_most of them
    // require that option: the cars requiring it are the set S of car types
    for (int o = 0; o < options; ++o) {
      std::vector<int> requiring;
      for (int t = 0; t < types; ++t)
        if (requires_option[t][o].get<int>() == 1) requiring.push_back(t);
      // no car requires this option, so the station is never overloaded
      if (requiring.empty()) continue;
      sequence(*this, seq, IntSet(requiring.data(), static_cast<int>(requiring.size())),
               per_slots[o], 0, at_most[o]);
    }

    branch(*this, seq, INT_VAR_AFC_SIZE_MAX(0.99), INT_VAL_MIN());
    restarts(100);
    output("sequence", seq);
  }

  CarSequencing(CarSequencing& s) : dcp::Space(s) { seq.update(*this, s.seq); }
  Gecode::Space* copy() override { return new CarSequencing(*this); }
};

DCP_MODEL(CarSequencing)
