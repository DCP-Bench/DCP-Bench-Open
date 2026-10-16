// Two jobs on one machine, no overlap, minimise the makespan. "Job 1 before job 2" or
// "job 2 before job 1" is a disjunction, so each order gets a binary and a big-M.
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
  const double d1 = 3, d2 = 4;
  // Safe big-M: in an optimal schedule with no idle time the starts are at most the total
  // work, so no start needs to exceed d1 + d2. The starts are bounded by it.
  const double big_m = d1 + d2;

  Highs h;
  h.setOptionValue("output_flag", false);
  h.setOptionValue("threads", HighsInt{1});
  h.setOptionValue("mip_rel_gap", 0.0);
  h.setOptionValue("mip_abs_gap", 0.0);

  HighsInt s1 = column(h, 0, big_m, false), s2 = column(h, 0, big_m, false);
  HighsInt makespan = column(h, 0, kHighsInf, false);
  HighsInt first_is_1 = column(h, 0, 1, true);  // 1: job 1 before job 2

  row(h, {s1, makespan}, {1, -1}, -kHighsInf, -d1);        // s1 + d1 <= C
  row(h, {s2, makespan}, {1, -1}, -kHighsInf, -d2);        // s2 + d2 <= C
  // first_is_1 = 1: s1 + d1 <= s2. Written as s1 - s2 + M b <= M - d1.
  row(h, {s1, s2, first_is_1}, {1, -1, big_m}, -kHighsInf, big_m - d1);
  // first_is_1 = 0: s2 + d2 <= s1. Written as s2 - s1 - M b <= -d2.
  row(h, {s2, s1, first_is_1}, {1, -1, -big_m}, -kHighsInf, -d2);

  h.changeColCost(makespan, 1);
  h.changeObjectiveSense(ObjSense::kMinimize);

  h.run();
  if (h.getModelStatus() != HighsModelStatus::kOptimal) {
    std::printf("not solved: %s\n", h.modelStatusToString(h.getModelStatus()).c_str());
    return 1;
  }
  const auto& x = h.getSolution().col_value;
  std::printf("Makespan: %.0f\n", h.getInfo().objective_function_value);
  std::printf("start job 1: %.0f, start job 2: %.0f\n", x[s1], x[s2]);
  return 0;
}
