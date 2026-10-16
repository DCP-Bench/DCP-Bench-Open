// All n-queens placements. Integer column c[i] is the column of the queen in row i, linked to
// binaries x[i][j]. Each solution is excluded with a no-good over the c columns (skill recipe).
#include <cmath>
#include <cstdio>
#include <fstream>
#include <vector>

#include <nlohmann/json.hpp>

#include "Highs.h"

static void row(Highs& h, const std::vector<HighsInt>& cols, const std::vector<double>& coefs, double lo, double hi) {
  h.addRow(lo, hi, static_cast<HighsInt>(cols.size()), cols.data(), coefs.data());
}

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
  const int n = data.at("n").get<int>();

  Highs h;
  h.setOptionValue("output_flag", false);
  h.setOptionValue("threads", HighsInt{1});
  h.setOptionValue("mip_rel_gap", 0.0);
  h.setOptionValue("mip_abs_gap", 0.0);

  // Columns: c[i] = i (integer 0..n-1); x[i][j] = n + i * n + j (binary).
  auto X = [n](int i, int j) { return static_cast<HighsInt>(n + i * n + j); };
  for (int i = 0; i < n; ++i) {
    h.addVar(0, n - 1);
    h.changeColIntegrality(i, HighsVarType::kInteger);
  }
  for (int k = 0; k < n * n; ++k) {
    h.addVar(0, 1);
    h.changeColIntegrality(n + k, HighsVarType::kInteger);
  }

  for (int i = 0; i < n; ++i) {
    // One queen per row, and c[i] = sum_j j x[i][j].
    std::vector<HighsInt> cols;
    std::vector<double> ones;
    for (int j = 0; j < n; ++j) { cols.push_back(X(i, j)); ones.push_back(1); }
    row(h, cols, ones, 1, 1);
    cols.assign(1, i);
    std::vector<double> link = {1};
    for (int j = 0; j < n; ++j) { cols.push_back(X(i, j)); link.push_back(-j); }
    row(h, cols, link, 0, 0);
  }
  // At most one queen per column.
  for (int j = 0; j < n; ++j) {
    std::vector<HighsInt> cols;
    std::vector<double> ones;
    for (int i = 0; i < n; ++i) { cols.push_back(X(i, j)); ones.push_back(1); }
    row(h, cols, ones, -kHighsInf, 1);
  }
  // At most one queen per diagonal and anti-diagonal.
  for (int d = 0; d <= 2 * n - 2; ++d) {
    std::vector<HighsInt> cols;
    std::vector<double> ones;
    for (int i = 0; i < n; ++i) {
      int j = d - i;
      if (j >= 0 && j < n) { cols.push_back(X(i, j)); ones.push_back(1); }
    }
    row(h, cols, ones, -kHighsInf, 1);
  }
  for (int d = -(n - 1); d <= n - 1; ++d) {
    std::vector<HighsInt> cols;
    std::vector<double> ones;
    for (int i = 0; i < n; ++i) {
      int j = i - d;
      if (j >= 0 && j < n) { cols.push_back(X(i, j)); ones.push_back(1); }
    }
    row(h, cols, ones, -kHighsInf, 1);
  }

  std::vector<HighsInt> cols(n);
  for (int i = 0; i < n; ++i) cols[i] = i;

  while (true) {
    h.run();
    if (h.getModelStatus() != HighsModelStatus::kOptimal) break;
    const std::vector<double>& sol = h.getSolution().col_value;
    std::vector<double> values(n);
    std::printf("{\"queens\": [");
    for (int i = 0; i < n; ++i) {
      values[i] = std::round(sol[i]);
      std::printf("%s%d", i ? ", " : "", static_cast<int>(values[i]));
    }
    std::printf("]}\n");
    forbid(h, cols, values, 0, n - 1);
  }
  return 0;
}
