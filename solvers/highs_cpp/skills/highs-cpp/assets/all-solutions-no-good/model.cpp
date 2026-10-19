// All solutions of x + y = 2 with 0 <= x, y <= 2. HiGHS has no solution pool, so
// each solution is excluded by a no-good over the integer columns and the model is
// solved again until it is infeasible.
#include <cmath>
#include <cstdio>
#include <vector>

#include "Highs.h"

HighsInt integer(Highs& h, double lo, double hi) {
  HighsInt k = h.getNumCol();
  h.addVar(lo, hi);
  h.changeColIntegrality(k, HighsVarType::kInteger);
  return k;
}

void row(Highs& h, const std::vector<HighsInt>& cols, const std::vector<double>& coefs, double lo, double hi) {
  h.addRow(lo, hi, static_cast<HighsInt>(cols.size()), cols.data(), coefs.data());
}

// Forbids the current values of cols: at least one column must differ from its value.
// For a column with value v in [lo, hi], a binary b_below forces col <= v - 1 when it
// is 1, and a binary b_above forces col >= v + 1 when it is 1. The big-M constants come
// from the column's own bounds, so they are as small as they can be.
void forbid(Highs& h, const std::vector<HighsInt>& cols, const std::vector<double>& values,
            double lo, double hi) {
  std::vector<HighsInt> any;
  std::vector<double> ones;
  for (std::size_t i = 0; i < cols.size(); ++i) {
    double v = values[i];
    if (v > lo) {  // col + (hi - v + 1) * below <= hi
      HighsInt below = integer(h, 0, 1);
      row(h, {cols[i], below}, {1, hi - v + 1}, -kHighsInf, hi);
      any.push_back(below);
      ones.push_back(1);
    }
    if (v < hi) {  // col - (v + 1 - lo) * above >= lo
      HighsInt above = integer(h, 0, 1);
      row(h, {cols[i], above}, {1, -(v + 1 - lo)}, lo, kHighsInf);
      any.push_back(above);
      ones.push_back(1);
    }
  }
  row(h, any, ones, 1, kHighsInf);  // at least one indicator: the assignment is excluded
}

int main() {
  const double lo = 0, hi = 2;
  Highs h;
  h.setOptionValue("output_flag", false);
  h.setOptionValue("threads", HighsInt{1});
  HighsInt x = integer(h, lo, hi), y = integer(h, lo, hi);
  row(h, {x, y}, {1, 1}, 2, 2);

  int count = 0;
  while (true) {
    h.run();
    if (h.getModelStatus() != HighsModelStatus::kOptimal) break;
    double vx = std::round(h.getSolution().col_value[x]);
    double vy = std::round(h.getSolution().col_value[y]);
    std::printf("x = %g, y = %g\n", vx, vy);
    ++count;
    forbid(h, {x, y}, {vx, vy}, lo, hi);
  }
  std::printf("Solutions: %d (last status: %s)\n", count, h.modelStatusToString(h.getModelStatus()).c_str());
  return 0;
}
