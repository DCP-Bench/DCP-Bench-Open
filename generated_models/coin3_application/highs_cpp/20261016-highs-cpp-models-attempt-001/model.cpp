// Coin problem: find the fewest coins that let one pay every amount from 1 up to
// max_amount_to_pay - 1 with the given denominations. x[i] is the number of coins
// of denomination i that are carried.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  std::vector<int> denom = instance.at("denominations").get<std::vector<int>>();
  int max_amount = instance.at("max_amount_to_pay").get<int>();
  int n = static_cast<int>(denom.size());

  // number of coins of each denomination; no more than max_amount coins of one kind can be useful
  std::vector<dcp::Lin> x(n);
  for (int i = 0; i < n; ++i) x[i] = dcp::new_var(h, 0, max_amount);

  // every amount v from 1 to max_amount - 1 is paid with coins that are carried:
  // y[v][i] coins of denomination i are handed over for amount v
  for (int v = 1; v <= max_amount - 1; ++v) {
    std::vector<dcp::Lin> y(n);
    for (int i = 0; i < n; ++i) {
      int hi = v / denom[i];  // at most v / d_i coins of denomination i fit in amount v
      y[i] = dcp::new_var(h, 0, hi);
    }

    // the coins handed over for amount v add up to exactly v
    dcp::Lin paid = 0;
    for (int i = 0; i < n; ++i) paid = paid + denom[i] * y[i];
    dcp::add_row(h, paid, v, v);

    // only coins that are carried can be handed over: y[v][i] <= x[i]
    for (int i = 0; i < n; ++i) dcp::add_row(h, y[i] - x[i], -kHighsInf, 0);
  }

  // the total number of coins carried is minimised
  dcp::Lin total = 0;
  for (int i = 0; i < n; ++i) total = total + x[i];
  out.minimize(total);

  out.add("x", x);
}
