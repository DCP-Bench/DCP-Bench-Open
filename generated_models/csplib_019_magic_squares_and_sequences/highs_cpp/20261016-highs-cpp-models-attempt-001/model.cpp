// Magic sequence of length n: x_0..x_{n-1} with values between 0 and n-1, such that
// for each i the number i occurs exactly x_i times in the sequence.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n").get<int>();

  // y[j][v] = 1 when position j holds the value v (0..n-1).
  std::vector<std::vector<dcp::Lin>> y(n, std::vector<dcp::Lin>(n));
  for (int j = 0; j < n; ++j)
    for (int v = 0; v < n; ++v) y[j][v] = dcp::new_var(h, 0, 1);

  // x_j = value at position j, the sum of v * y[j][v].
  std::vector<dcp::Lin> x(n);
  for (int j = 0; j < n; ++j)
    for (int v = 0; v < n; ++v) x[j] = x[j] + v * y[j][v];

  // each position holds exactly one value
  for (int j = 0; j < n; ++j) {
    dcp::Lin one_value;
    for (int v = 0; v < n; ++v) one_value = one_value + y[j][v];
    dcp::add_row(h, one_value, 1, 1);
  }

  // the number i occurs exactly x_i times in the sequence
  for (int i = 0; i < n; ++i) {
    dcp::Lin occurrences;
    for (int j = 0; j < n; ++j) occurrences = occurrences + y[j][i];
    dcp::add_row(h, occurrences - x[i], 0, 0);
  }

  out.add("x", x);
}
