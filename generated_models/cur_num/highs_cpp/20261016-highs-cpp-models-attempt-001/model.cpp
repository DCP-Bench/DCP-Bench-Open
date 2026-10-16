// Problem cur_num: find a number p between 1 and 10000 such that p + 1 is a
// square and p/2 + 1 is a square, other than 48. The output is peculiar = p.
// Satisfaction problem, no instance fields.
//
// Write p = 2h, with h between 1 and 5000. Then p + 1 = 2h + 1 must be a square
// s^2 and p/2 + 1 = h + 1 must be a square t^2.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  (void)instance;

  // h is half of the number: p = 2h, 1 <= p <= 10000
  dcp::Lin hv = dcp::new_var(h, 1, 5000);

  // the number must be another one than 48, so h is not 24
  // b = 1 means h is at most 23, b = 0 means h is at least 25
  dcp::Lin b = dcp::new_var(h, 0, 1);
  dcp::add_row(h, hv + 5000.0 * b, -kHighsInf, 5023);
  dcp::add_row(h, hv + 25.0 * b, 25, kHighsInf);

  // the number plus 1 is a square: 2h + 1 = s^2 with s between 0 and 100
  // one-hot choice of s, y[k] = 1 means s = k
  std::vector<dcp::Lin> y;
  dcp::Lin one_s = 0.0;
  dcp::Lin sq_s = 0.0;
  for (int k = 0; k <= 100; ++k) {
    y.push_back(dcp::new_var(h, 0, 1));
    one_s = one_s + y[k];
    sq_s = sq_s + (double)(k * k) * y[k];
  }
  // exactly one value for s
  dcp::add_row(h, one_s, 1, 1);
  // s squared is 2h + 1
  dcp::add_row(h, sq_s - 2.0 * hv, 1, 1);

  // half of the number plus 1 is a square: h + 1 = t^2 with t between 0 and 70
  // one-hot choice of t, z[j] = 1 means t = j
  std::vector<dcp::Lin> z;
  dcp::Lin one_t = 0.0;
  dcp::Lin sq_t = 0.0;
  for (int j = 0; j <= 70; ++j) {
    z.push_back(dcp::new_var(h, 0, 1));
    one_t = one_t + z[j];
    sq_t = sq_t + (double)(j * j) * z[j];
  }
  // exactly one value for t
  dcp::add_row(h, one_t, 1, 1);
  // t squared is h + 1
  dcp::add_row(h, sq_t - hv, 1, 1);

  out.add("peculiar", 2.0 * hv);
}
