// Four numbers: given up to four distinct integers between 1 and 10, find three integers
// (also between 1 and 10) such that every given number is a sum of a subset of the three.
// Output x: the three integers.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const json& numbers = instance.at("numbers");
  const int n = static_cast<int>(numbers.size());  // how many numbers this instance gives
  const int k = 3;                                 // the answer has three integers
  const double top = 10;                           // the description bounds every value by 1..10

  // the three integers, each between 1 and 10
  std::vector<dcp::Lin> x;
  for (int j = 0; j < k; ++j) x.push_back(dcp::new_var(h, 1, top));

  for (int i = 0; i < n; ++i) {
    const double target = numbers[i].get<double>();

    // the given number is the sum of the chosen integers that are picked for it
    dcp::Lin total;
    for (int j = 0; j < k; ++j) {
      // picked[i][j] = 1 if chosen integer j is used to make given number i
      dcp::Lin picked = dcp::new_var(h, 0, 1);
      // used = x[j] when picked, else 0
      dcp::Lin used = dcp::new_var(h, 0, top);

      // an integer that is not picked contributes 0: used <= 10 picked
      dcp::add_row(h, used - top * picked, -kHighsInf, 0);
      // used is at most the chosen integer: used <= x[j]
      dcp::add_row(h, used - x[j], -kHighsInf, 0);
      // a picked integer contributes its full value: used >= x[j] - 10 (1 - picked)
      dcp::add_row(h, used - x[j] - top * picked, -top, kHighsInf);

      total = total + used;
    }
    // the given number equals the sum of the contributions for it
    dcp::add_row(h, total, target, target);
  }

  out.add("x", x);
}
