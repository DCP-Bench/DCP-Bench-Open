// N-queens, one solution. x[i][j] binary: queen in row i, column j.
#include <cstdio>
#include <fstream>
#include <vector>

#include <nlohmann/json.hpp>

#include "Highs.h"

int main(int argc, char** argv) {
  if (argc < 2) return 1;
  std::ifstream file(argv[1]);
  nlohmann::json data = nlohmann::json::parse(file);
  const int n = data.at("n").get<int>();

  Highs h;
  h.setOptionValue("output_flag", false);
  h.setOptionValue("threads", HighsInt{1});
  h.setOptionValue("mip_rel_gap", 0.0);
  h.setOptionValue("mip_abs_gap", 0.0);

  auto X = [n](int i, int j) { return static_cast<HighsInt>(i * n + j); };
  for (int k = 0; k < n * n; ++k) {
    h.addVar(0, 1);
    h.changeColIntegrality(k, HighsVarType::kInteger);
  }

  // One queen per row.
  for (int i = 0; i < n; ++i) {
    std::vector<HighsInt> cols;
    std::vector<double> ones;
    for (int j = 0; j < n; ++j) { cols.push_back(X(i, j)); ones.push_back(1); }
    h.addRow(1, 1, n, cols.data(), ones.data());
  }
  // At most one queen per column.
  for (int j = 0; j < n; ++j) {
    std::vector<HighsInt> cols;
    std::vector<double> ones;
    for (int i = 0; i < n; ++i) { cols.push_back(X(i, j)); ones.push_back(1); }
    h.addRow(-kHighsInf, 1, n, cols.data(), ones.data());
  }
  // At most one queen on each diagonal (i + j constant) and anti-diagonal (i - j constant).
  for (int d = 0; d <= 2 * n - 2; ++d) {
    std::vector<HighsInt> cols;
    std::vector<double> ones;
    for (int i = 0; i < n; ++i) {
      int j = d - i;
      if (j >= 0 && j < n) { cols.push_back(X(i, j)); ones.push_back(1); }
    }
    h.addRow(-kHighsInf, 1, static_cast<HighsInt>(cols.size()), cols.data(), ones.data());
  }
  for (int d = -(n - 1); d <= n - 1; ++d) {
    std::vector<HighsInt> cols;
    std::vector<double> ones;
    for (int i = 0; i < n; ++i) {
      int j = i - d;
      if (j >= 0 && j < n) { cols.push_back(X(i, j)); ones.push_back(1); }
    }
    h.addRow(-kHighsInf, 1, static_cast<HighsInt>(cols.size()), cols.data(), ones.data());
  }

  h.run();
  if (h.getModelStatus() == HighsModelStatus::kInfeasible) {
    std::printf("{\"status\": \"unsatisfiable\"}\n");
    return 0;
  }
  if (h.getModelStatus() != HighsModelStatus::kOptimal) {
    std::fprintf(stderr, "not solved: %s\n", h.modelStatusToString(h.getModelStatus()).c_str());
    return 1;
  }

  const std::vector<double>& val = h.getSolution().col_value;
  std::printf("{\"queens\": [");
  for (int i = 0; i < n; ++i) {
    int col = 0;
    for (int j = 0; j < n; ++j) {
      if (val[X(i, j)] > 0.5) { col = j; break; }
    }
    std::printf("%s%d", i ? ", " : "", col);
  }
  std::printf("]}\n");
  return 0;
}
