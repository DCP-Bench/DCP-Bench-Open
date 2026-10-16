// All optimal 0/1 knapsack selections. Solve for the optimum z, pin the value to z,
// then enumerate the selections with no-goods over the item columns.
#include <cmath>
#include <cstdio>
#include <fstream>
#include <numeric>
#include <vector>

#include <nlohmann/json.hpp>

#include "Highs.h"

static void row(Highs& h, const std::vector<HighsInt>& cols, const std::vector<double>& coefs, double lo, double hi) {
  h.addRow(lo, hi, static_cast<HighsInt>(cols.size()), cols.data(), coefs.data());
}

// Forbids the current values of cols (skill recipe): for a column with value v in [lo, hi],
// a binary below forces col <= v - 1 when 1, a binary above forces col >= v + 1 when 1.
static void forbid(Highs& h, const std::vector<HighsInt>& cols, const std::vector<double>& values,
                   double lo, double hi) {
  std::vector<HighsInt> any;
  std::vector<double> ones;
  for (std::size_t i = 0; i < cols.size(); ++i) {
    double v = values[i];
    if (v > lo) {
      HighsInt below = h.getNumCol();
      h.addVar(0, 1);
      h.changeColIntegrality(below, HighsVarType::kInteger);
      row(h, {cols[i], below}, {1, hi - v + 1}, -kHighsInf, hi);
      any.push_back(below);
      ones.push_back(1);
    }
    if (v < hi) {
      HighsInt above = h.getNumCol();
      h.addVar(0, 1);
      h.changeColIntegrality(above, HighsVarType::kInteger);
      row(h, {cols[i], above}, {1, -(v + 1 - lo)}, lo, kHighsInf);
      any.push_back(above);
      ones.push_back(1);
    }
  }
  row(h, any, ones, 1, kHighsInf);
}

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
  std::iota(cols.begin(), cols.end(), 0);
  for (int i = 0; i < n; ++i) {
    h.addVar(0, 1);
    h.changeColIntegrality(i, HighsVarType::kInteger);
    h.changeColCost(i, value[i]);
  }
  row(h, cols, weight, -kHighsInf, capacity);

  h.run();
  if (h.getModelStatus() != HighsModelStatus::kOptimal) {
    std::fprintf(stderr, "not solved: %s\n", h.modelStatusToString(h.getModelStatus()).c_str());
    return 1;
  }
  double z = std::round(h.getInfo().objective_function_value);

  // Pin the objective to the optimum.
  row(h, cols, value, z - 1e-5, z + 1e-5);

  while (true) {
    h.run();
    if (h.getModelStatus() != HighsModelStatus::kOptimal) break;
    const std::vector<double>& sol = h.getSolution().col_value;
    std::vector<double> vals(n);
    std::printf("{\"take\": [");
    for (int i = 0; i < n; ++i) {
      vals[i] = std::round(sol[i]);
      std::printf("%s%d", i ? ", " : "", static_cast<int>(vals[i]));
    }
    std::printf("]}\n");
    forbid(h, cols, vals, 0, 1);
  }
  return 0;
}
