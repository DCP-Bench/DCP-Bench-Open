// Hanging weights puzzle: weights A..M hang from a system of bars. Each weight is an
// integer between 1 and 13. The weights on either side of a pivot must balance when
// weighted by distance from the pivot, and a bar hanging beneath another contributes
// its total weight as if it were a single weight. Find the weights a..m that balance
// the diagram as shown. A satisfaction problem with no instance data.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  // Each weight has an integer value between 1 and 13.
  dcp::Lin a = dcp::new_var(h, 1, 13);
  dcp::Lin b = dcp::new_var(h, 1, 13);
  dcp::Lin c = dcp::new_var(h, 1, 13);
  dcp::Lin d = dcp::new_var(h, 1, 13);
  dcp::Lin e = dcp::new_var(h, 1, 13);
  dcp::Lin f = dcp::new_var(h, 1, 13);
  dcp::Lin g = dcp::new_var(h, 1, 13);
  dcp::Lin hw = dcp::new_var(h, 1, 13);
  dcp::Lin i = dcp::new_var(h, 1, 13);
  dcp::Lin j = dcp::new_var(h, 1, 13);
  dcp::Lin k = dcp::new_var(h, 1, 13);
  dcp::Lin l = dcp::new_var(h, 1, 13);
  dcp::Lin m = dcp::new_var(h, 1, 13);

  // Bottom right bar: 5*C = D (C hangs five units from its pivot, D one unit).
  dcp::add_row(h, 5 * c - d, 0, 0);

  // The bar above it, which carries G and the bar holding C and D: 3*G = 2*(C+D).
  dcp::add_row(h, 3 * g - 2 * (c + d), 0, 0);

  // Bottom left bar: A and B balance about the pivot, 4*A = B.
  dcp::add_row(h, 4 * a - b, 0, 0);

  // Bar holding E and F: 3*E = 2*F.
  dcp::add_row(h, 3 * e - 2 * f, 0, 0);

  // Bar holding H, the bar holding E and F, and I: 3*H = 2*(E+F) + 3*I.
  dcp::add_row(h, 3 * hw - 2 * (e + f) - 3 * i, 0, 0);

  // Bar holding L and M, with the bar holding H, I, E and F hanging at its left end:
  // L + 4*M = H + I + E + F.
  dcp::add_row(h, l + 4 * m - (hw + i + e + f), 0, 0);

  // Bar holding J and K, with the bars holding A, B and G, C, D hanging beneath it:
  // 3*(A+B) + 2*J = K + 2*(G+C+D).
  dcp::add_row(h, 3 * (a + b) + 2 * j - k - 2 * (g + c + d), 0, 0);

  // Top bar: the bar holding L and M, and the bar holding J, K, A, B, G, C, D balance
  // about the pivot: 4*(L+M+H+I+E+F) = 3*(J+K+A+B+G+C+D).
  dcp::add_row(h, 4 * (l + m + hw + i + e + f) - 3 * (j + k + a + b + g + c + d), 0, 0);

  out.add("a", a);
  out.add("b", b);
  out.add("c", c);
  out.add("d", d);
  out.add("e", e);
  out.add("f", f);
  out.add("g", g);
  out.add("h", hw);
  out.add("i", i);
  out.add("j", j);
  out.add("k", k);
  out.add("l", l);
  out.add("m", m);
}
