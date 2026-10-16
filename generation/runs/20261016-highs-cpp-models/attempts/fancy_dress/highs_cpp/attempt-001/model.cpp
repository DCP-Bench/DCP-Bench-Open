// fancy_dress: Mr Greenguest chooses which green items to wear (tie t, hat h,
// shirt r, socks s) and whether he pays the entrance fee n, minimising the cost.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  (void)instance;  // the problem has no instance data
  dcp::Lin t = dcp::new_var(h, 0, 1);  // green tie
  dcp::Lin hat = dcp::new_var(h, 0, 1);  // green hat
  dcp::Lin r = dcp::new_var(h, 0, 1);  // green shirt
  dcp::Lin s = dcp::new_var(h, 0, 1);  // green socks
  dcp::Lin n = dcp::new_var(h, 0, 1);  // entrance fee paid

  // If someone wears a green tie he has to wear a green shirt,
  // unless he pays the entrance fee.
  dcp::add_row(h, t - r - n, -kHighsInf, 0);

  // A guest may only wear green socks and a green shirt if he wears a green tie
  // or a green hat, unless he pays the entrance fee.
  dcp::add_row(h, s + r - t - hat - n, -kHighsInf, 1);

  // A guest wearing a green shirt or a green hat or who does not wear green socks
  // must wear a green tie, unless he pays the entrance fee.
  // Written as r + h + (1 - s) <= 3 t + 3 n.
  dcp::add_row(h, r + hat - s - 3 * t - 3 * n, -kHighsInf, -1);

  // Cost: tie 10, hat 2, socks 12, entrance fee 11. The owned shirt costs nothing.
  out.minimize(10 * t + 2 * hat + 12 * s + 11 * n);

  out.add("h", hat);
  out.add("n", n);
  out.add("r", r);
  out.add("s", s);
  out.add("t", t);
}
