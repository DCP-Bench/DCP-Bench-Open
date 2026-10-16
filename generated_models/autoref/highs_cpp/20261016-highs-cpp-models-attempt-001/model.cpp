#include "dcp.h"

// The series S has n+2 entries s_0..s_{n+1}. Each entry is an index from 0 to n,
// coded as one-hot binaries y[j][v] (the value is sum_v v * y[j][v]).
void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n").get<int>();
  int m = instance.at("m").get<int>();
  int len = n + 2;
  int top = n;

  std::vector<std::vector<dcp::Lin>> y(len, std::vector<dcp::Lin>(top + 1));
  for (int j = 0; j < len; j++)
    for (int v = 0; v <= top; v++) y[j][v] = dcp::new_var(h, 0, 1);

  // every entry s_j takes exactly one value
  std::vector<dcp::Lin> s(len);
  for (int j = 0; j < len; j++) {
    dcp::Lin one_value;
    dcp::Lin value;
    for (int v = 0; v <= top; v++) {
      one_value = one_value + y[j][v];
      value = value + static_cast<double>(v) * y[j][v];
    }
    dcp::add_row(h, one_value, 1, 1);
    s[j] = value;
  }

  // the last entry s_{n+1} equals m (no solution when m is outside the value range)
  if (m > top)
    dcp::add_row(h, dcp::Lin(0), 1, 1);
  else
    dcp::add_row(h, y[len - 1][m], 1, 1);

  // for each i from 0 to n, s_i is the number of entries equal to i
  for (int i = 0; i <= n; i++) {
    dcp::Lin count;
    for (int j = 0; j < len; j++) count = count + y[j][i];
    dcp::add_row(h, count - s[i], 0, 0);
  }

  out.add("s", s);
}
