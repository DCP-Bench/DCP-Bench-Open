#include <string>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Cabling: place the devices in the slots of a rack, one per slot, so that the
// total length of all the cables connecting them is as short as possible.  A
// cable's length is the distance between its two devices times its multiplicity.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n = instance.at("n").get<int>();
  const std::vector<std::string> devices =
      instance.at("devices").get<std::vector<std::string>>();
  // Each cable entry is [device name, device name, number of cables].
  const json& cable_struct = instance.at("cable_struct");
  const int num_cables = static_cast<int>(cable_struct.size());

  // Device name -> index in devices.
  auto device_index = [&](const std::string& name) {
    for (int i = 0; i < static_cast<int>(devices.size()); ++i) {
      if (devices[i] == name) return i;
    }
    return -1;
  };

  int64_t total_cables = 0;
  for (const json& c : cable_struct) total_cables += c.at(2).get<int64_t>();

  // x[d]: position of device d in the rack (0..n-1).
  std::vector<IntVar> x;
  for (int d = 0; d < n; ++d) x.push_back(model.NewIntVar(Domain(0, n - 1)));
  // t[i]: length of cable group i; the reference bounds it by 1..n*n.
  std::vector<IntVar> t;
  for (int i = 0; i < num_cables; ++i) {
    t.push_back(model.NewIntVar(Domain(1, static_cast<int64_t>(n) * n)));
  }
  // final_sum: total length of all cables, bounded as in the reference.
  IntVar final_sum = model.NewIntVar(
      Domain(0, static_cast<int64_t>(n) * n * total_cables));

  // All devices have distinct positions in the rack.
  model.AddAllDifferent(x);

  // The total length is the sum of the individual cable lengths.
  LinearExpr all_lengths;
  for (int i = 0; i < num_cables; ++i) all_lengths += t[i];
  model.AddEquality(final_sum, all_lengths);

  // A cable group's length is the distance between the positions of its two
  // devices, times the number of cables in the group.
  for (int i = 0; i < num_cables; ++i) {
    const int a = device_index(cable_struct[i].at(0).get<std::string>());
    const int b = device_index(cable_struct[i].at(1).get<std::string>());
    const int64_t num = cable_struct[i].at(2).get<int64_t>();
    IntVar distance = model.NewIntVar(Domain(0, n - 1));
    model.AddAbsEquality(distance, x[a] - x[b]);
    model.AddEquality(t[i], num * distance);
  }

  // Make the total cable length as short as possible.
  model.Minimize(final_sum);

  outputs = {{"final_sum", final_sum.index()}};
}
