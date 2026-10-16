// An integer x in 0..5 with 2 x = 7 has no solution. HiGHS reports Infeasible from
// getModelStatus(); run() itself returns kOk.
#include <cstdio>

#include "Highs.h"

int main() {
  Highs h;
  h.setOptionValue("output_flag", false);
  h.setOptionValue("threads", HighsInt{1});
  h.addVar(0, 5);
  h.changeColIntegrality(0, HighsVarType::kInteger);
  HighsInt index[1] = {0};
  double value[1] = {2};
  h.addRow(7, 7, 1, index, value);

  HighsStatus run = h.run();
  std::printf("run returned: %d\n", static_cast<int>(run));
  std::printf("Status: %s\n", h.modelStatusToString(h.getModelStatus()).c_str());
  return 0;
}
