// Probe: can the driver capture HiGHS error messages while output_flag is off?
#include "Highs.h"
#include <iostream>
#include <string>

static std::string captured;

static void on_log(int type, const std::string& message, const HighsCallbackOutput* out,
                   HighsCallbackInput* in, void* data) {
  (void)out; (void)in; (void)data;
  if (type == (int)HighsLogType::kError || type == (int)HighsLogType::kWarning) captured += message;
}

int main() {
  {  // lower bound above upper bound
    Highs h;
    h.setOptionValue("output_flag", false);
    h.setCallback(on_log, nullptr);
    h.startCallback(kCallbackLogging);
    h.addVar(5, 1);
    HighsStatus s = h.run();
    std::cout << "bad bounds: status=" << (int)s << " model=" << h.modelStatusToString(h.getModelStatus())
              << " captured=[" << captured << "]\n";
    captured.clear();
  }
  {  // invalid option value
    Highs h;
    h.setOptionValue("output_flag", false);
    h.setCallback(on_log, nullptr);
    h.startCallback(kCallbackLogging);
    HighsStatus s = h.setOptionValue("threads", (HighsInt)1);
    std::cout << "set threads: " << (int)s << "\n";
    HighsStatus t = h.setOptionValue("no_such_option", (HighsInt)1);
    std::cout << "bad option: " << (int)t << " captured=[" << captured << "]\n";
    captured.clear();
  }
  {  // non-integer coefficient row with infinite bounds: warning expected?
    Highs h;
    h.setOptionValue("output_flag", false);
    h.setCallback(on_log, nullptr);
    h.startCallback(kCallbackLogging);
    h.addVar(0, 1);
    HighsInt idx[1] = {0};
    double val[1] = {1e-12};
    h.addRow(-kHighsInf, kHighsInf, 1, idx, val);
    HighsStatus s = h.run();
    std::cout << "tiny coef: status=" << (int)s << " model=" << h.modelStatusToString(h.getModelStatus())
              << " captured=[" << captured << "]\n";
    captured.clear();
  }
  return 0;
}
