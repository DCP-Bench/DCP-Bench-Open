// Probe: with output_flag on and console logging off, does the callback capture errors?
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
  {
    Highs h;
    h.setOptionValue("output_flag", true);
    h.setOptionValue("log_to_console", false);
    h.setCallback(on_log, nullptr);
    h.startCallback(kCallbackLogging);
    HighsStatus t = h.setOptionValue("no_such_option", (HighsInt)1);
    std::cout << "bad option: " << (int)t << " captured=[" << captured << "]\n";
    captured.clear();
    h.addVar(5, 1);
    HighsStatus s = h.run();
    std::cout << "bad bounds: status=" << (int)s << " captured=[" << captured << "]\n";
    captured.clear();
    HighsInt idx[1] = {0};
    double val[1] = {1.0};
    HighsStatus r = h.addRow(0.0, 1.0, 1, idx, val);
    std::cout << "row on col 0: " << (int)r << " captured=[" << captured << "]\n";
    captured.clear();
    HighsStatus q = h.addRow(0.0, 1.0, 1, idx, val);
    HighsInt badidx[1] = {7};
    HighsStatus p = h.addRow(0.0, 1.0, 1, badidx, val);
    std::cout << "row on bad col: " << (int)p << " captured=[" << captured << "]\n";
    (void)q;
  }
  return 0;
}
