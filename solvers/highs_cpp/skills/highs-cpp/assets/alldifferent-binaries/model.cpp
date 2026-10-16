// Four variables x0..x3 with values in 1..4, all different, with x0 > x1 and
// minimise x0 + 2 x1 + 3 x2 + 4 x3. The optimum is x = (4, 3, 2, 1), objective 20. Each x_i is the value of its one-hot binaries,
// and every value is used at most once across the variables.
#include <cmath>
#include <cstdio>
#include <vector>

#include "Highs.h"

HighsInt binary(Highs& h) {
  HighsInt k = h.getNumCol();
  h.addVar(0, 1);
  h.changeColIntegrality(k, HighsVarType::kInteger);
  return k;
}

void row(Highs& h, const std::vector<HighsInt>& cols, const std::vector<double>& coefs, double lo, double hi) {
  h.addRow(lo, hi, static_cast<HighsInt>(cols.size()), cols.data(), coefs.data());
}

int main() {
  const int vars = 4, values = 4;
  Highs h;
  h.setOptionValue("output_flag", false);
  h.setOptionValue("threads", HighsInt{1});
  h.setOptionValue("mip_rel_gap", 0.0);
  h.setOptionValue("mip_abs_gap", 0.0);

  // y[i][v] = 1 when x_i takes value v + 1.
  std::vector<std::vector<HighsInt>> y(vars, std::vector<HighsInt>(values));
  for (auto& line : y)
    for (auto& column : line) column = binary(h);

  // x_i = sum_v (v + 1) y[i][v] is a new continuous column tied by a row.
  std::vector<HighsInt> x(vars);
  for (int i = 0; i < vars; ++i) {
    x[i] = h.getNumCol();
    h.addVar(1, values);
    std::vector<HighsInt> cols = {x[i]};
    std::vector<double> coefs = {-1};
    for (int v = 0; v < values; ++v) { cols.push_back(y[i][v]); coefs.push_back(v + 1); }
    row(h, cols, coefs, 0, 0);  // x_i - sum (v + 1) y[i][v] = 0
    std::vector<HighsInt> one_hot;
    std::vector<double> ones;
    for (int v = 0; v < values; ++v) { one_hot.push_back(y[i][v]); ones.push_back(1); }
    row(h, one_hot, ones, 1, 1);  // exactly one value per variable
  }
  for (int v = 0; v < values; ++v) {  // all different: each value used by at most one variable
    std::vector<HighsInt> used;
    std::vector<double> ones;
    for (int i = 0; i < vars; ++i) { used.push_back(y[i][v]); ones.push_back(1); }
    row(h, used, ones, -kHighsInf, 1);
  }
  row(h, {x[0], x[1]}, {1, -1}, 1, kHighsInf);  // x0 > x1 for integers: x0 - x1 >= 1

  std::vector<double> weights = {1, 2, 3, 4};
  for (int i = 0; i < vars; ++i) h.changeColCost(x[i], weights[i]);
  h.changeObjectiveSense(ObjSense::kMinimize);

  h.run();
  if (h.getModelStatus() != HighsModelStatus::kOptimal) {
    std::printf("not solved: %s\n", h.modelStatusToString(h.getModelStatus()).c_str());
    return 1;
  }
  const auto& value = h.getSolution().col_value;
  std::printf("x = [%.0f, %.0f, %.0f, %.0f]\n", std::round(value[x[0]]), std::round(value[x[1]]),
              std::round(value[x[2]]), std::round(value[x[3]]));
  std::printf("Objective: %.0f\n", std::round(h.getInfo().objective_function_value));
  return 0;
}
