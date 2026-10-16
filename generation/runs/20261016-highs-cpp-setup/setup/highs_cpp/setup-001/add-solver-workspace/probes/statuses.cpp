// Probe: model statuses for infeasible, unbounded, unbounded-or-infeasible,
// empty-row infeasibility, time limit, and feasibility status of optimal MIPs.
#include "Highs.h"
#include <iostream>
#include <vector>

static void report(const char* label, Highs& h, HighsStatus s) {
  std::cout << label << ": run=" << (int)s << " model=" << h.modelStatusToString(h.getModelStatus())
            << " primal_status=" << h.getInfo().primal_solution_status
            << " obj=" << h.getInfo().objective_function_value << "\n";
}

static void base(Highs& h) {
  h.setOptionValue("output_flag", false);
  h.setOptionValue("threads", 1);
  h.setOptionValue("mip_rel_gap", 0.0);
  h.setOptionValue("mip_abs_gap", 0.0);
}

int main() {
  {  // infeasible integer model: 2x = 1
    Highs h; base(h);
    h.addVar(0, 10); h.changeColIntegrality(0, HighsVarType::kInteger);
    HighsInt idx[1] = {0}; double val[1] = {2.0};
    h.addRow(1.0, 1.0, 1, idx, val);
    report("infeasible", h, h.run());
  }
  {  // unbounded integer model: maximise x, x >= 0 integer, no rows
    Highs h; base(h);
    h.addVar(0, kHighsInf); h.changeColIntegrality(0, HighsVarType::kInteger);
    h.changeColCost(0, 1.0); h.changeObjectiveSense(ObjSense::kMaximize);
    report("unbounded", h, h.run());
  }
  {  // unbounded-or-infeasible: needs presolve detection; try with a row
    Highs h; base(h);
    h.addVar(-kHighsInf, kHighsInf); h.addVar(-kHighsInf, kHighsInf);
    h.changeColIntegrality(0, HighsVarType::kInteger); h.changeColIntegrality(1, HighsVarType::kInteger);
    h.changeColCost(0, -1.0); h.changeColCost(1, -1.0); h.changeObjectiveSense(ObjSense::kMinimize);
    HighsInt idx[2] = {0, 1}; double val[2] = {1.0, -1.0};
    h.addRow(0.0, kHighsInf, 2, idx, val);
    report("unb-or-inf candidate", h, h.run());
  }
  {  // empty row with bounds excluding zero
    Highs h; base(h);
    h.addVar(0, 1);
    h.addRow(1.0, 1.0, 0, nullptr, nullptr);
    report("empty row infeasible", h, h.run());
  }
  {  // empty row feasible, zero-column model with one row
    Highs h; base(h);
    h.addRow(-1.0, 1.0, 0, nullptr, nullptr);
    report("empty row feasible, no cols", h, h.run());
  }
  {  // time limit 0.0 is inf; set tiny limit on a hard-ish MIP: knapsack-like
    Highs h; base(h);
    const int n = 60;
    HighsInt idx[n]; double val[n], w[n];
    for (int i = 0; i < n; ++i) {
      h.addVar(0, 1); h.changeColIntegrality(i, HighsVarType::kInteger);
      h.changeColCost(i, -(double)((i * 37) % 23 + 10));
      idx[i] = i; val[i] = (double)((i * 53) % 31 + 5); w[i] = val[i];
    }
    h.addRow(-kHighsInf, 200.0, n, idx, val);
    h.setOptionValue("time_limit", 0.05);
    report("time limit", h, h.run());
  }
  {  // value beyond 32 bits and negative offset
    Highs h; base(h);
    h.addVar(0, 5e9); h.changeColIntegrality(0, HighsVarType::kInteger);
    h.changeColCost(0, -1.0); h.changeObjectiveOffset(-3.0e9);
    h.changeObjectiveSense(ObjSense::kMinimize);
    HighsInt idx[1] = {0}; double val[1] = {1.0};
    h.addRow(3123456789.0, kHighsInf, 1, idx, val);
    report("big value", h, h.run());
    std::cout << "  x=" << h.getSolution().col_value[0] << "\n";
  }
  return 0;
}
