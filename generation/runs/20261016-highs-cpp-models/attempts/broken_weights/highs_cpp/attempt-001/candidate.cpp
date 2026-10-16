#include "dcp.h"

// Broken weight: the merchant's n pieces have whole-pound weights that sum to the total m, and
// every whole weight from 1 to m can be weighed by putting pieces on both pans of a balance.
void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int m = instance.at("m").get<int>();  // total weight in pounds
  int n = instance.at("n").get<int>();  // number of pieces

  // the weight of each piece is a whole number of pounds from 1 to the total
  std::vector<dcp::Lin> weights;
  for (int i = 0; i < n; ++i) weights.push_back(dcp::new_var(h, 1, m));

  // the pieces together weigh the total weight
  dcp::Lin total;
  for (int i = 0; i < n; ++i) total = total + weights[i];
  dcp::add_row(h, total, m, m);

  // every whole weight k from 1 to the total can be balanced by the pieces
  // (p = 1: the piece is on the object's pan, q = 1: the piece is on the other pan, neither: unused)
  // Big-M constants: |y - w| and |y + w| are at most 2m since 1 <= w <= m and -m <= y <= m.
  double bigM = 2.0 * m;
  for (int k = 1; k <= m; ++k) {
    dcp::Lin signed_sum;
    for (int i = 0; i < n; ++i) {
      dcp::Lin p = dcp::new_var(h, 0, 1);
      dcp::Lin q = dcp::new_var(h, 0, 1);
      // a piece is on at most one pan
      dcp::add_row(h, p + q, -kHighsInf, 1);

      // y is the piece's signed contribution: +w on the other pan, -w on the object's pan, 0 unused
      dcp::Lin y = dcp::new_var(h, -m, m);
      // if the piece is on the object's pan (p = 1), then y = -w
      dcp::add_row(h, y + weights[i] + bigM * p, -kHighsInf, bigM);
      dcp::add_row(h, y + weights[i] - bigM * p, -bigM, kHighsInf);
      // if the piece is on the other pan (q = 1), then y = w
      dcp::add_row(h, y - weights[i] + bigM * q, -kHighsInf, bigM);
      dcp::add_row(h, y - weights[i] - bigM * q, -bigM, kHighsInf);
      // if the piece is unused (p = q = 0), then y = 0
      dcp::add_row(h, y - m * p - m * q, -kHighsInf, 0);
      dcp::add_row(h, y + m * p + m * q, 0, kHighsInf);
      signed_sum = signed_sum + y;
    }
    dcp::add_row(h, signed_sum, k, k);
  }

  out.add("weights", weights);
}
