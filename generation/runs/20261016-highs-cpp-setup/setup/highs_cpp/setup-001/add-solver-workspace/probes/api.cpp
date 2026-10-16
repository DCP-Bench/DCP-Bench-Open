#include "Highs.h"
#include <iostream>
int main() {
  Highs h;
  std::cout << "version " << h.version() << " githash " << h.githash() << "\n";
  h.setOptionValue("output_flag", false);
  double tl; h.getOptionValue("time_limit", tl); std::cout << "time_limit default " << tl << "\n";
  double rg; h.getOptionValue("mip_rel_gap", rg); std::cout << "mip_rel_gap default " << rg << "\n";
  double ag; h.getOptionValue("mip_abs_gap", ag); std::cout << "mip_abs_gap default " << ag << "\n";
  double ft; h.getOptionValue("mip_feasibility_tolerance", ft); std::cout << "mip_feas default " << ft << "\n";
  HighsInt th; h.getOptionValue("threads", th); std::cout << "threads default " << th << "\n";
  HighsInt rs; h.getOptionValue("random_seed", rs); std::cout << "random_seed default " << rs << "\n";
  // empty model
  HighsStatus s = h.run();
  std::cout << "empty run status " << (int)s << " model " << h.modelStatusToString(h.getModelStatus()) << "\n";
  // one int col, objective offset, maximise
  Highs g; g.setOptionValue("output_flag", false);
  g.addVar(0, 5); g.changeColIntegrality(0, HighsVarType::kInteger);
  g.changeColCost(0, -2.0); g.changeObjectiveOffset(7.5); g.changeObjectiveSense(ObjSense::kMaximize);
  s = g.run();
  std::cout << "run status " << (int)s << " model " << g.modelStatusToString(g.getModelStatus()) << " obj " << g.getInfo().objective_function_value << " x " << g.getSolution().col_value[0] << "\n";
  std::cout << "mip_gap " << g.getInfo().mip_gap << " infinity " << g.getInfinity() << "\n";
  return 0;
}
