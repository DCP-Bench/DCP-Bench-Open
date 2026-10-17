// Candies: give each of n children in a row at least one candy, more to a child rated higher
// than an adjacent child, minimising the total number of candies.
// Outputs: x (candies per child) and z (total candies).
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const auto& ratings = instance.at("ratings");
  int n = static_cast<int>(ratings.size());

  // each child gets at least 1 candy; no child needs more than n candies
  std::vector<dcp::Lin> x;
  for (int i = 0; i < n; i++) x.push_back(dcp::new_var(h, 1, n));

  // two children next to each other: the one with the higher rating gets more candies
  for (int i = 0; i + 1 < n; i++) {
    int ri = ratings[i].get<int>();
    int rj = ratings[i + 1].get<int>();
    if (ri > rj) {
      // the left child has the higher rating, so it gets more candies than the right child
      dcp::add_row(h, x[i] - x[i + 1], 1, kHighsInf);
    } else if (ri < rj) {
      // the right child has the higher rating, so it gets more candies than the left child
      dcp::add_row(h, x[i + 1] - x[i], 1, kHighsInf);
    }
    // equal neighbours: no constraint
  }

  // total number of candies, to be minimised
  dcp::Lin total;
  for (const auto& v : x) total = total + v;

  out.add("x", x);
  out.add("z", total);
  out.minimize(total);
}
