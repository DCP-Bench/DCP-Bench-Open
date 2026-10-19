// Chess set production: a joinery makes small and large boxwood chess sets each week.
// Decide how many sets of each kind to make so as to maximise profit.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  // number of small sets made per week, a whole number
  dcp::Lin small = dcp::new_var(h, 0, 160);
  // number of large sets made per week, a whole number
  dcp::Lin large = dcp::new_var(h, 0, 160);

  // lathe hours: a small set needs 3 hours, a large set 2 hours, at most 160 lathe-hours per week
  dcp::add_row(h, 3 * small + 2 * large, -kHighsInf, 160);
  // boxwood: a small set needs 1 kg, a large set 3 kg, at most 200 kg per week
  dcp::add_row(h, 1 * small + 3 * large, -kHighsInf, 200);

  // profit: a small set yields $5, a large set $20; maximise the total profit
  dcp::Lin profit = 5 * small + 20 * large;
  out.maximize(profit);

  out.add("small_set", small);
  out.add("large_set", large);
  out.add("max_profit", profit);
}
