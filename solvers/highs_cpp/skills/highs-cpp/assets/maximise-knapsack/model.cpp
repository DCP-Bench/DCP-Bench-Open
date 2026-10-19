// 0/1 knapsack: maximise the value of the chosen items plus a fixed bonus of 100.
// The bonus is the objective's constant offset; the weights and values are
// negative-free here, and the offset is set with changeObjectiveOffset.
#include <cmath>
#include <cstdio>
#include <vector>

#include "Highs.h"

int main() {
  const std::vector<double> value = {6, 5, 8, 9, 6, 7, 3};
  const std::vector<double> weight = {2, 3, 6, 7, 5, 9, 4};
  const double capacity = 9;
  const int n = static_cast<int>(value.size());

  Highs h;
  h.setOptionValue("output_flag", false);
  h.setOptionValue("threads", HighsInt{1});
  h.setOptionValue("mip_rel_gap", 0.0);  // OPTIMAL then means proven optimal
  h.setOptionValue("mip_abs_gap", 0.0);

  std::vector<HighsInt> cols(n);
  for (int i = 0; i < n; ++i) {
    cols[i] = i;
    h.addVar(0, 1);
    h.changeColIntegrality(i, HighsVarType::kInteger);
    h.changeColCost(i, value[i]);  // maximise: the cost is the value
  }
  h.changeObjectiveSense(ObjSense::kMaximize);
  h.changeObjectiveOffset(100);
  h.addRow(-kHighsInf, capacity, n, cols.data(), weight.data());

  h.run();
  if (h.getModelStatus() != HighsModelStatus::kOptimal) {
    std::printf("not solved: %s\n", h.modelStatusToString(h.getModelStatus()).c_str());
    return 1;
  }
  const auto& x = h.getSolution().col_value;
  std::printf("Maximum value: %.0f\n", std::round(h.getInfo().objective_function_value));
  for (int i = 0; i < n; ++i)
    if (std::lround(x[i]) == 1) std::printf("take item %d\n", i);
  return 0;
}
