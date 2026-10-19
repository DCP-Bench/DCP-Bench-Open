// x + y = 7 with 0 <= x, y <= 7. Minimise |x - y| + max(x, y) + 10 * p, where
//   p = b1 * b2 is a product of binaries,
//   b1 = 1 exactly when x >= 4, b2 = 1 exactly when y >= 4 (indicators from both sides).
#include <cmath>
#include <cstdio>
#include <vector>

#include "Highs.h"

HighsInt column(Highs& h, double lo, double hi, bool integer) {
  HighsInt k = h.getNumCol();
  h.addVar(lo, hi);
  if (integer) h.changeColIntegrality(k, HighsVarType::kInteger);
  return k;
}

void row(Highs& h, const std::vector<HighsInt>& cols, const std::vector<double>& coefs, double lo, double hi) {
  h.addRow(lo, hi, static_cast<HighsInt>(cols.size()), cols.data(), coefs.data());
}

int main() {
  Highs h;
  h.setOptionValue("output_flag", false);
  h.setOptionValue("threads", HighsInt{1});
  h.setOptionValue("mip_rel_gap", 0.0);
  h.setOptionValue("mip_abs_gap", 0.0);

  HighsInt x = column(h, 0, 7, true), y = column(h, 0, 7, true);
  row(h, {x, y}, {1, 1}, 7, 7);

  // z = |x - y|: z >= x - y and z >= y - x. Minimising pushes z down to the true value.
  HighsInt z = column(h, 0, kHighsInf, false);
  row(h, {z, x, y}, {1, -1, 1}, 0, kHighsInf);   // z >= x - y
  row(h, {z, x, y}, {1, 1, -1}, 0, kHighsInf);   // z >= y - x

  // m = max(x, y): m >= x and m >= y.
  HighsInt m = column(h, 0, kHighsInf, false);
  row(h, {m, x}, {1, -1}, 0, kHighsInf);
  row(h, {m, y}, {1, -1}, 0, kHighsInf);

  // b1 = (x >= 4): x - 4 b1 >= 0 and x - 4 b1 <= 3. Same for b2 and y.
  HighsInt b1 = column(h, 0, 1, true), b2 = column(h, 0, 1, true);
  row(h, {x, b1}, {1, -4}, 0, kHighsInf);
  row(h, {x, b1}, {1, -4}, -kHighsInf, 3);
  row(h, {y, b2}, {1, -4}, 0, kHighsInf);
  row(h, {y, b2}, {1, -4}, -kHighsInf, 3);

  // p = b1 * b2: p <= b1, p <= b2, p >= b1 + b2 - 1.
  HighsInt p = column(h, 0, 1, true);
  row(h, {p, b1}, {1, -1}, -kHighsInf, 0);
  row(h, {p, b2}, {1, -1}, -kHighsInf, 0);
  row(h, {p, b1, b2}, {1, -1, -1}, -1, kHighsInf);

  // Objective: z + m + 10 p. Each term has coefficient 1 or 10.
  h.changeColCost(z, 1);
  h.changeColCost(m, 1);
  h.changeColCost(p, 10);
  h.changeObjectiveSense(ObjSense::kMinimize);

  h.run();
  if (h.getModelStatus() != HighsModelStatus::kOptimal) {
    std::printf("not solved: %s\n", h.modelStatusToString(h.getModelStatus()).c_str());
    return 1;
  }
  const auto& v = h.getSolution().col_value;
  std::printf("Objective: %.0f\n", std::round(h.getInfo().objective_function_value));
  std::printf("x = %.0f, y = %.0f, product p = %.0f\n", std::round(v[x]), std::round(v[y]), std::round(v[p]));
  return 0;
}
