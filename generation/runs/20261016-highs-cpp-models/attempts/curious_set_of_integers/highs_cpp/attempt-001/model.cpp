// Curious set of integers: find a number x >= 0 that, together with 1, 3, 8 and 120,
// makes every product of two members one less than a perfect square.
// The fifth number is x, bounded by the instance's max_val.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  long long max_val = instance.at("max_val").get<long long>();

  // the fifth number is between 0 and max_val
  dcp::Lin x = dcp::new_var(h, 0, static_cast<double>(max_val));

  const long long members[4] = {1, 3, 8, 120};
  for (long long a : members) {
    // the product of x and a member, one less than a perfect square
    // (the product of a and x is one less than a perfect square s^2);
    // s ranges over the roots that a x + 1 can reach for x in 0..max_val
    long long top = a * max_val + 1;
    long long root = 0;
    while ((root + 1) * (root + 1) <= top) root++;

    // one binary per candidate root s in 1..root: exactly one is chosen
    std::vector<dcp::Lin> pick;
    for (long long s = 1; s <= root; s++) pick.push_back(dcp::new_var(h, 0, 1));

    // exactly one root is picked
    dcp::Lin count = 0;
    for (const auto& b : pick) count = count + b;
    dcp::add_row(h, count, 1, 1);

    // the product of a and x is one less than the picked square
    // (a x + 1 = sum of s^2 times the binary for s)
    dcp::Lin square = 0;
    for (long long s = 1; s <= root; s++) square = square + static_cast<double>(s * s) * pick[s - 1];
    dcp::add_row(h, static_cast<double>(a) * x - square, -1, -1);
  }

  out.add("number", x);
}
