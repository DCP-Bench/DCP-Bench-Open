// Twelve-pack problem: given a target number of items, choose how many packs of each
// size to use so that the total meets or exceeds the target, as close to it as possible.
// Output counts: the number of packs used of each size, in the order of the packs field.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  std::vector<int> packs = instance.at("packs").get<std::vector<int>>();
  int target = instance.at("target").get<int>();
  const size_t k = packs.size();

  // one count per pack size; a count above ceil(target / size) never helps an optimal solution
  std::vector<dcp::Lin> counts;
  for (size_t i = 0; i < k; ++i) {
    int upper = (target + packs[i] - 1) / packs[i];
    counts.push_back(dcp::new_var(h, 0, upper));
  }

  // the packs together hold at least the target number of items
  dcp::Lin total;
  for (size_t i = 0; i < k; ++i) total = total + packs[i] * counts[i];
  dcp::add_row(h, total, target, kHighsInf);

  // the total is as small as possible, so the excess over the target is minimal
  out.minimize(total);
  out.add("counts", counts);
}
