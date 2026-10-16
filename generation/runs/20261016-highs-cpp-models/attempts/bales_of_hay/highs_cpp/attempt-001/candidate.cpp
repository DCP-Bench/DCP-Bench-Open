#include <algorithm>
#include <stdexcept>
#include <vector>

#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const int n = instance.at("n").get<int>();
  const std::vector<int> pair_sum = instance.at("weights").get<std::vector<int>>();
  const int m = static_cast<int>(pair_sum.size());
  if (m != n * (n - 1) / 2) throw std::runtime_error("weights must hold one entry per pair of bales");

  // Each bale weight is a whole number from 0 up to the heaviest pair sum. Weights are not
  // negative, so every bale is at most the heaviest pair sum.
  const int heaviest = *std::max_element(pair_sum.begin(), pair_sum.end());
  std::vector<dcp::Lin> bale;
  for (int i = 0; i < n; ++i) bale.push_back(dcp::new_var(h, 0, heaviest));

  // The pairs of bales, in order (i, j) with i < j. Pair p is the p-th such pair.
  std::vector<std::pair<int, int>> pairs;
  for (int i = 0; i < n; ++i)
    for (int j = i + 1; j < n; ++j) pairs.push_back({i, j});

  // Each pair of bales takes exactly one of the given pair sums: y[p][k] = 1 when pair p
  // has the sum weights[k]. Each given sum is used by exactly one pair.
  std::vector<std::vector<dcp::Lin>> y(m, std::vector<dcp::Lin>(m));
  for (int p = 0; p < m; ++p)
    for (int k = 0; k < m; ++k) y[p][k] = dcp::new_var(h, 0, 1);

  // every pair of bales has exactly one sum
  for (int p = 0; p < m; ++p) {
    dcp::Lin e;
    for (int k = 0; k < m; ++k) e = e + y[p][k];
    dcp::add_row(h, e, 1, 1);
  }
  // every given sum belongs to exactly one pair of bales
  for (int k = 0; k < m; ++k) {
    dcp::Lin e;
    for (int p = 0; p < m; ++p) e = e + y[p][k];
    dcp::add_row(h, e, 1, 1);
  }

  // the two bales of a pair weigh together the sum assigned to that pair
  for (int p = 0; p < m; ++p) {
    dcp::Lin e = bale[pairs[p].first] + bale[pairs[p].second];
    for (int k = 0; k < m; ++k) e = e - static_cast<double>(pair_sum[k]) * y[p][k];
    dcp::add_row(h, e, 0, 0);
  }

  out.add("bales", bale);
}
