// Clock triplets: rearrange the numbers 1 to 12 on the face of a clock so that no
// triplet of adjacent numbers has a sum higher than 21. Output x lists the 12
// numbers in clock order, each from 1 to 12. The clock wraps around, so the
// triplets are taken cyclically.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  (void)instance;  // the clock has 12 positions and the numbers 1 to 12 in every instance
  const int n = 12;
  const int max_triplet_sum = 21;

  // position i holds number v+1 when y[i][v] = 1
  std::vector<std::vector<dcp::Lin>> y(n, std::vector<dcp::Lin>(n));
  for (int i = 0; i < n; ++i)
    for (int v = 0; v < n; ++v) y[i][v] = dcp::new_var(h, 0, 1);

  // the number on each position is one of 1 to 12
  std::vector<dcp::Lin> x(n);
  for (int i = 0; i < n; ++i) {
    x[i] = dcp::new_var(h, 1, n);
    dcp::Lin value;
    dcp::Lin one_hot;
    for (int v = 0; v < n; ++v) {
      value = value + (v + 1) * y[i][v];
      one_hot = one_hot + y[i][v];
    }
    // the number on position i is the value its one indicator selects
    dcp::add_row(h, x[i] - value, 0, 0);
    // each position takes exactly one value
    dcp::add_row(h, one_hot, 1, 1);
  }

  // the numbers 1 to 12 each appear once on the clock
  for (int v = 0; v < n; ++v) {
    dcp::Lin used;
    for (int i = 0; i < n; ++i) used = used + y[i][v];
    dcp::add_row(h, used, 1, 1);
  }

  // every triplet of adjacent numbers has a sum of at most 21, wrapping around the clock
  for (int i = 0; i < n; ++i) {
    dcp::Lin triplet = x[i] + x[(i + 1) % n] + x[(i + 2) % n];
    dcp::add_row(h, triplet, -kHighsInf, max_triplet_sum);
  }

  out.add("x", x);
}
