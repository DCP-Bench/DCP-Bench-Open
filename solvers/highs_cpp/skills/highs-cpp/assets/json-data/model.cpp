// Reads a 0/1 knapsack from JSON: {"capacity": 9, "values": [...], "weights": [...]}.
// The file is the first argument, or data.json in the working directory. Every size comes
// from the data; keys the model does not use are ignored.
#include <cstdio>
#include <fstream>
#include <string>
#include <vector>

#include <nlohmann/json.hpp>

#include "Highs.h"

int main(int argc, char** argv) {
  std::string path = argc > 1 ? argv[1] : "data.json";
  std::ifstream file(path);
  if (!file) {
    std::printf("cannot open %s\n", path.c_str());
    return 1;
  }
  nlohmann::json data = nlohmann::json::parse(file);
  std::vector<double> value = data.at("values").get<std::vector<double>>();
  std::vector<double> weight = data.at("weights").get<std::vector<double>>();
  double capacity = data.at("capacity").get<double>();
  const int n = static_cast<int>(value.size());

  Highs h;
  h.setOptionValue("output_flag", false);
  h.setOptionValue("threads", HighsInt{1});
  h.setOptionValue("mip_rel_gap", 0.0);
  h.setOptionValue("mip_abs_gap", 0.0);
  std::vector<HighsInt> cols(n);
  for (int i = 0; i < n; ++i) {
    cols[i] = i;
    h.addVar(0, 1);
    h.changeColIntegrality(i, HighsVarType::kInteger);
    h.changeColCost(i, value[i]);
  }
  h.changeObjectiveSense(ObjSense::kMaximize);
  h.addRow(-kHighsInf, capacity, n, cols.data(), weight.data());

  h.run();
  if (h.getModelStatus() != HighsModelStatus::kOptimal) {
    std::printf("not solved: %s\n", h.modelStatusToString(h.getModelStatus()).c_str());
    return 1;
  }
  std::printf("Value: %.0f with %d items\n", h.getInfo().objective_function_value, n);
  return 0;
}
