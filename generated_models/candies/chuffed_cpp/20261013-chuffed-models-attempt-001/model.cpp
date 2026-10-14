// Candies: give every child in a line at least one candy so that a child with a higher rating than a neighbour gets more candies, minimizing the total.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<int> ratings = instance.at("ratings").get<std::vector<int>>();
  int n = static_cast<int>(ratings.size());

  // x[i] is the number of candies of child i; every child gets at least 1 candy.
  // The upper bound n is enough: a chain of n children needs at most n candies at its top.
  vec<IntVar*> x;
  createVars(x, n, 1, n);

  // a child with a higher rating than the next child must get more candies than the next child,
  // and a child with a lower rating must get fewer; equal ratings impose no condition
  for (int i = 0; i + 1 < n; ++i) {
    if (ratings[i] > ratings[i + 1]) {
      int_rel(x[i], IRT_GT, x[i + 1]);
    } else if (ratings[i] < ratings[i + 1]) {
      int_rel(x[i], IRT_LT, x[i + 1]);
    }
  }

  // z is the total number of candies handed out
  IntVar* z = newIntVar(n, n * n);
  int_linear(x, IRT_EQ, z);

  // branch on the candies of each child from left to right, smallest first
  branch(x, VAR_INORDER, VAL_MIN);
  optimize(z, OPT_MIN);

  json xs = json::array();
  for (int i = 0; i < n; ++i) xs.push_back(dcp::out(x[i]));
  outputs = {{"x", xs}, {"z", dcp::out(z)}};
}
