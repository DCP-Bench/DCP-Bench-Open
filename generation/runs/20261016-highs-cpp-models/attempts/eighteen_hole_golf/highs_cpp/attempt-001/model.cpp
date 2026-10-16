// Eighteen-hole golf course: 18 holes, each of length 3, 4 or 5, total length 72.
// The instance carries no fields, so every constant here is from the problem statement.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  (void)instance;
  const int holes = 18;   // "a random 18-hole golf course"
  const int min_len = 3;  // "each hole has a length of 3, 4, or 5"
  const int max_len = 5;
  const int total = 72;   // "the total length of the course is 72"

  // holes[i] is the length of hole i, one integer column per hole
  std::vector<dcp::Lin> length;
  for (int i = 0; i < holes; i++) {
    length.push_back(dcp::new_var(h, min_len, max_len));
  }

  // the total length of the course is 72
  dcp::Lin sum;
  for (int i = 0; i < holes; i++) {
    sum = sum + length[i];
  }
  dcp::add_row(h, sum, total, total);

  // the lengths of the holes, as a list of 18 integers
  out.add("holes", length);
}
