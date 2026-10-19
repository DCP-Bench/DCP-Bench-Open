// Pythagorean triplet: natural numbers a, b, c with a^2 + b^2 = c^2 and a + b + c = 1000.
// Print (a, b, c). The triplet is unique when written with a < b < c.
#include "dcp.h"

// Squares are not linear, so each of a, b, c gets one binary per value in its range:
// s_v = 1 exactly when the number equals v. Then v^2 is the linear sum of v^2 * s_v.
// Returns the sum of v^2 * s_v and sets `value` to the integer column tied to the selectors.
static dcp::Lin squared_selection(Highs& h, int lo, int hi, dcp::Lin& value) {
  dcp::Lin x = dcp::new_var(h, lo, hi);
  dcp::Lin count, val_sum, sq_sum;
  for (int v = lo; v <= hi; ++v) {
    dcp::Lin s = dcp::new_var(h, 0, 1);
    count = count + s;
    val_sum = val_sum + static_cast<double>(v) * s;
    sq_sum = sq_sum + static_cast<double>(v * v) * s;
  }
  dcp::add_row(h, count, 1, 1);             // exactly one value is selected
  dcp::add_row(h, x - val_sum, 0, 0);       // the column equals the selected value
  value = x;
  return sq_sum;
}

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  (void)instance;  // the problem has no instance data

  // Natural numbers, ordered a < b < c. From a + b + c = 1000 and a < b < c:
  // a <= 332 (since 3a < 1000), b <= 499 (since 2b < 1000 - a), c <= 997 (since a, b >= 1).
  // c > 1000/3 because c is the largest, so c >= 334.
  dcp::Lin a, b, c;
  dcp::Lin sq_a = squared_selection(h, 1, 332, a);
  dcp::Lin sq_b = squared_selection(h, 2, 499, b);
  dcp::Lin sq_c = squared_selection(h, 334, 997, c);

  // a + b + c = 1000
  dcp::add_row(h, a + b + c, 1000, 1000);

  // a < b < c
  dcp::add_row(h, b - a, 1, kHighsInf);
  dcp::add_row(h, c - b, 1, kHighsInf);

  // a^2 + b^2 = c^2
  dcp::add_row(h, sq_a + sq_b - sq_c, 0, 0);

  out.add("a", a);
  out.add("b", b);
  out.add("c", c);
}
