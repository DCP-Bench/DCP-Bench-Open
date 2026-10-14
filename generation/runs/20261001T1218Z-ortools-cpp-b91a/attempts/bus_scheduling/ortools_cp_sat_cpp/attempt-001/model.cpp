#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Bus scheduling: the day is cut into 4-hour slots with a known bus demand per
// slot, and a bus works 8 successive hours (two slots).  Choose how many buses
// start in each slot so every slot's demand is met with as few buses as possible.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<int64_t> demands =
      instance.at("demands").get<std::vector<int64_t>>();
  const int slots = static_cast<int>(demands.size());

  int64_t total_demand = 0;
  for (const int64_t d : demands) total_demand += d;

  // x[i]: number of buses that start working in 4-hour slot i.  The reference
  // bounds it by the total demand.
  std::vector<IntVar> x;
  for (int i = 0; i < slots; ++i) {
    x.push_back(model.NewIntVar(Domain(0, total_demand)));
  }

  // A bus covers its starting slot and the next one (the day wraps around), so
  // the buses that started in slot i and in slot i + 1 must meet the demand of
  // slot i + 1.
  for (int i = 0; i < slots; ++i) {
    const int next = (i + 1) % slots;
    model.AddGreaterOrEqual(x[i] + x[next], demands[next]);
  }

  // Use as few buses as possible in total.
  LinearExpr buses;
  for (int i = 0; i < slots; ++i) buses += x[i];
  model.Minimize(buses);

  json x_out = json::array();
  for (const IntVar& v : x) x_out.push_back(v.index());
  outputs = {{"x", x_out}};
}
