// 0/1 knapsack: take[i] binary, maximise total value under the capacity.
#include <cmath>
#include <cstdio>
#include <fstream>
#include <vector>

#include <nlohmann/json.hpp>

#include "Highs.h"

int main(int argc, char** argv) {
  if (argc < 2) return 1;
  std::ifstream file(argv[1]);
  nlohmann::json data = nlohmann::json::parse(file);
  std::vector<double> weight = data.at("weights").get<std::vector<double>>();
  std::vector<double> value = data.at("values").get<std::vector<double>>();
  double capacity = data.at("capacity").get<double>();
  const int n = static_cast<int>(value.size());

  Highs h;
  h.setOptionValue("output_flag", false);
  h.setOptionValue("threads", HighsInt{1});
  h.setOptionValue("mip_rel_gap", 0.0);
  h.setOptionValue("mip_abs_gap", 0.0);
  h.changeObjectiveSense(ObjSense::kMaximize);

  std::vector<HighsInt> cols(n);
  for (int i = 0; i < n; ++i) {
    cols[i] = i;
    h.addVar(0, 1);
    h.changeColIntegrality(i, HighsVarType::kInteger);
    h.changeColCost(i, value[i]);
  }
  h.addRow(-kHighsInf, capacity, n, cols.data(), weight.data());

  h.run();
  if (h.getModelStatus() != HighsModelStatus::kOptimal) {
    std::fprintf(stderr, "not solved: %s\n", h.modelStatusToString(h.getModelStatus()).c_str());
    return 1;
  }

  const std::vector<double>& val = h.getSolution().col_value;
  std::printf("{\"take\": [");
  for (int i = 0; i < n; ++i) std::printf("%s%d", i ? ", " : "", std::lround(val[i]) ? 1 : 0);
  std::printf("]}\n");
  return 0;
}
