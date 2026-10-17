// Among: n variables x[i] in 0..7; exactly m of them must take a value from the set v.
// Output: the array x.
#include "dcp.h"

#include <set>

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n").get<int>();
  int m = instance.at("m").get<int>();
  const int lo_val = 0;
  const int hi_val = 7;

  // the distinct values of v that lie in the allowed range 0..7
  std::set<int> allowed;
  for (const auto& value : instance.at("v")) {
    int v = value.get<int>();
    if (v >= lo_val && v <= hi_val) allowed.insert(v);
  }

  // x[i] is one of 0..7, coded by binaries y[i][k] with x[i] = k
  std::vector<std::vector<dcp::Lin>> y(n);
  std::vector<dcp::Lin> x(n);
  for (int i = 0; i < n; i++) {
    // every value of x is between 0 and 7, so exactly one indicator of x[i] is on
    dcp::Lin one_hot;
    dcp::Lin value;
    for (int k = lo_val; k <= hi_val; k++) {
      y[i].push_back(dcp::new_var(h, 0, 1, true));
      one_hot = one_hot + y[i][k];
      value = value + static_cast<double>(k) * y[i][k];
    }
    dcp::add_row(h, one_hot, 1, 1);
    x[i] = value;
  }

  // requires exactly m values in x to take one of the values in v
  dcp::Lin in_v;
  for (int i = 0; i < n; i++) {
    for (int k : allowed) in_v = in_v + y[i][k];
  }
  dcp::add_row(h, in_v, m, m);

  out.add("x", x);
}
