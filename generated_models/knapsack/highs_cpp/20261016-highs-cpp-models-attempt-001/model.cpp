// 0/1 knapsack: a hiker chooses which items to take into a backpack of limited
// weight capacity, maximising the total value of the items taken.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  // the item values, the item weights and the capacity come from the instance
  std::vector<int> values = instance.at("values").get<std::vector<int>>();
  std::vector<int> weights = instance.at("weights").get<std::vector<int>>();
  int capacity = instance.at("capacity");
  int n = static_cast<int>(values.size());

  // x[i] = 1 if item i is taken into the backpack
  std::vector<dcp::Lin> x;
  for (int i = 0; i < n; i++) {
    x.push_back(dcp::new_var(h, 0, 1));
  }

  // the total weight of the items taken must not exceed the weight capacity
  dcp::Lin total_weight = 0;
  for (int i = 0; i < n; i++) {
    total_weight = total_weight + weights[i] * x[i];
  }
  dcp::add_row(h, total_weight, -kHighsInf, capacity);

  // the total value of the items taken is the objective to maximise
  dcp::Lin total_value = 0;
  for (int i = 0; i < n; i++) {
    total_value = total_value + values[i] * x[i];
  }
  out.maximize(total_value);

  out.add("x", x);
}
