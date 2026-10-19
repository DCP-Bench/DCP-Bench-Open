// Five brigands (Alfonso A, Benito B, Carlos C, Diego D, Esteban E) hold exactly 200
// doubloons altogether. If Alfonso had twelve times as much, Benito three times as
// much, Carlos the same amount, Diego half as much and Esteban one-third as much,
// they would still have altogether just 200 doubloons. No brigand has less than one
// doubloon. Output the number of doubloons of each brigand (A, B, C, D, E).
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  (void)instance;

  // every brigand has at least one doubloon; the total is at most 200 since the others have at least one each
  dcp::Lin A = dcp::new_var(h, 1, 200);
  dcp::Lin B = dcp::new_var(h, 1, 200);
  dcp::Lin C = dcp::new_var(h, 1, 200);
  dcp::Lin D = dcp::new_var(h, 1, 200);
  dcp::Lin E = dcp::new_var(h, 1, 200);

  // they captured altogether exactly 200 doubloons
  dcp::add_row(h, A + B + C + D + E, 200, 200);

  // with twelve times A, three times B, C the same, half of D and one-third of E, the total is still 200;
  // multiplied by 6 so that every coefficient is an integer:
  // 72 A + 18 B + 6 C + 3 D + 2 E = 1200
  dcp::add_row(h, 72 * A + 18 * B + 6 * C + 3 * D + 2 * E, 1200, 1200);

  out.add("A", A);
  out.add("B", B);
  out.add("C", C);
  out.add("D", D);
  out.add("E", E);
}
