#include "dcp.h"

// Pilot fixture for highs_cpp: x + y == n, or x + y >= n minimised when optimize is set.
void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n");
  dcp::Lin x = dcp::new_var(h, 0, n);
  dcp::Lin y = dcp::new_var(h, 0, n);
  if (instance.at("optimize").get<bool>()) {
    dcp::add_row(h, x + y, n, kHighsInf);
    out.minimize(x + y);
  } else {
    dcp::add_row(h, x + y, n, n);
  }
  out.add("x", x);
  out.add("y", y);
}
