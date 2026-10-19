// Probe: the SKILL Quick start verbatim, plus the time-limit status and option defaults.
#include <cmath>
#include <cstdio>
#include "Highs.h"

int main() {
  {
    Highs h;
    h.setOptionValue("output_flag", false);
    h.setOptionValue("mip_rel_gap", 0.0);
    h.addVar(0, 4); h.addVar(0, 4);
    h.changeColIntegrality(0, HighsVarType::kInteger);
    h.changeColIntegrality(1, HighsVarType::kInteger);
    h.changeColCost(0, 1); h.changeColCost(1, 2);
    h.changeObjectiveSense(ObjSense::kMinimize);
    HighsInt cols[2] = {0, 1}; double coefs[2] = {1, 1};
    h.addRow(3, kHighsInf, 2, cols, coefs);
    h.run();
    if (h.getModelStatus() == HighsModelStatus::kOptimal)
      std::printf("Objective: %.0f\n", std::round(h.getInfo().objective_function_value));
  }
  {
    // knapsack-like hard MIP with a tiny time limit: expect kTimeLimit
    Highs h;
    h.setOptionValue("output_flag", false);
    h.setOptionValue("threads", HighsInt{1});
    const int n = 120;
    std::vector<HighsInt> idx(n);
    std::vector<double> val(n);
    for (int i = 0; i < n; ++i) {
      h.addVar(0, 1);
      h.changeColIntegrality(i, HighsVarType::kInteger);
      h.changeColCost(i, -(double)((i * 37) % 23 + 10));
      idx[i] = i; val[i] = (double)((i * 53) % 31 + 5);
    }
    h.addRow(-kHighsInf, 400.0, n, idx.data(), val.data());
    h.addRow(-kHighsInf, 350.0, n, idx.data(), val.data());
    h.setOptionValue("time_limit", 0.2);
    h.run();
    std::printf("time limit: %s primal=%d\n", h.modelStatusToString(h.getModelStatus()).c_str(),
                (int)h.getInfo().primal_solution_status);
  }
  {
    Highs h;
    bool flag = true; h.getOptionValue("output_flag", flag);
    bool log = true; h.getOptionValue("log_to_console", log);
    std::printf("default output_flag=%d log_to_console=%d\n", (int)flag, (int)log);
  }
  return 0;
}
