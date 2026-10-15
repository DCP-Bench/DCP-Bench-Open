// Cabling: place n devices in the slots of one rack, one device per slot, so that
// the sum over all cables of (cable count x distance in U between the two devices)
// is as small as possible. Output: final_sum, the optimal total cable length.
#include "dcp.h"

class Cabling : public dcp::Space {
 protected:
  IntVarArray pos;   // pos[d]: rack slot of device d (slots 0..n-1, 1U each)
  IntVar total;      // total cable length

 public:
  explicit Cabling(const json& instance) {
    int n = instance.at("n").get<int>();
    std::vector<std::string> devices = instance.at("devices").get<std::vector<std::string>>();
    // cable_struct rows are [device, device, number of cables]; devices are named
    // by the instance's "devices" list.
    const json& cable_struct = instance.at("cable_struct");

    pos = IntVarArray(*this, n, 0, n - 1);

    // every device has its own slot
    distinct(*this, pos, IPL_DOM);

    // cable length = distance in U between the slots of its two ends;
    // a line with k cables costs k times that length
    IntVarArgs lengths;
    IntArgs counts;
    for (const auto& row : cable_struct) {
      std::string from = row[0].get<std::string>();
      std::string to = row[1].get<std::string>();
      int k = row[2].get<int>();
      int a = -1, b = -1;
      for (int d = 0; d < n; ++d) {
        if (devices[d] == from) a = d;
        if (devices[d] == to) b = d;
      }
      lengths << expr(*this, abs(pos[a] - pos[b]), IPL_DOM);
      counts << k;
    }

    // sum of all cable lengths (every cable counted)
    total = expr(*this, sum(counts, lengths));

    branch(*this, pos, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    minimize(total);
    output("final_sum", total);
  }

  Cabling(Cabling& s) : dcp::Space(s) {
    pos.update(*this, s.pos);
    total.update(*this, s.total);
  }
  Gecode::Space* copy() override { return new Cabling(*this); }
};

DCP_MODEL(Cabling)
