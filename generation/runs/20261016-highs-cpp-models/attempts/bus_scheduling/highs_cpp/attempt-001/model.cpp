// Bus scheduling: buses are timetabled over successive 4-hour slots in a day. Each bus
// works 8 successive hours, so a bus that starts in slot i covers slots i and i+1.
// The day wraps around, so the last slot's buses carry into the first slot.
// Minimise the total number of buses.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const std::vector<int> demands = instance.at("demands").get<std::vector<int>>();
  const int n = static_cast<int>(demands.size());

  int total_demand = 0;
  for (int d : demands) total_demand += d;

  // x[i] = number of buses starting in slot i
  std::vector<dcp::Lin> x;
  for (int i = 0; i < n; i++) x.push_back(dcp::new_var(h, 0, total_demand));

  // the buses on duty in each slot must meet the demand for that slot:
  // the buses starting in this slot plus the buses starting in the previous slot (cyclic)
  for (int i = 0; i < n; i++) {
    int prev = (i + n - 1) % n;
    dcp::add_row(h, x[i] + x[prev], demands[i], kHighsInf);
  }

  // minimise the total number of buses
  dcp::Lin total;
  for (int i = 0; i < n; i++) total = total + x[i];
  out.minimize(total);

  // print the number of buses scheduled in each time slot
  out.add("x", x);
}
