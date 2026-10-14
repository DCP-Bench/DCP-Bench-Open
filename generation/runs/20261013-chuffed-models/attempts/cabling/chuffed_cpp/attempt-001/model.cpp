// Cabling: place the devices in one rack in a row, so that the total length of all
// cables (cable count times the distance between the two devices) is as short as possible.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<std::string> devices = instance.at("devices").get<std::vector<std::string>>();
  int n = static_cast<int>(devices.size());

  // position of each device in the rack, 0 .. n-1 (one device per slot)
  vec<IntVar*> pos;
  createVars(pos, n, 0, n - 1);

  // no two devices share a slot
  all_different(pos);

  // each cable bundle joins two devices and carries a number of cables
  json cables = instance.at("cable_struct");
  vec<IntVar*> lengths;
  vec<int> counts;
  for (const auto& c : cables) {
    std::string a = c[0].get<std::string>();
    std::string b = c[1].get<std::string>();
    int k = c[2].get<int>();
    int ia = -1, ib = -1;
    for (int i = 0; i < n; ++i) {
      if (devices[i] == a) ia = i;
      if (devices[i] == b) ib = i;
    }

    // d = position of a minus position of b
    IntVar* d = newIntVar(-(n - 1), n - 1);
    int_minus(pos[ia], pos[ib], d);

    // len = distance between the two devices along the rack
    IntVar* len = newIntVar(0, n - 1);
    int_abs(d, len);

    lengths.push(len);
    counts.push(k);
  }

  // total = sum over all cables of count times length
  int max_total = 0;
  for (int i = 0; i < counts.size(); ++i) max_total += counts[i] * (n - 1);
  IntVar* total = newIntVar(0, max_total);
  int_linear(counts, lengths, IRT_EQ, total);

  // the total cable length must be as short as possible
  branch(pos, VAR_INORDER, VAL_MIN);
  optimize(total, OPT_MIN);

  outputs = {{"final_sum", dcp::out(total)}};
}
