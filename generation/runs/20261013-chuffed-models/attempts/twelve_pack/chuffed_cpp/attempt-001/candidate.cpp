// Twelve pack: choose how many packs of each size to buy so that the total number of items meets or exceeds the target with the fewest items.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int target = instance.at("target");
  std::vector<int> pack_sizes = instance.at("packs").get<std::vector<int>>();
  int kinds = static_cast<int>(pack_sizes.size());
  int largest = 0;
  for (int s : pack_sizes) if (s > largest) largest = s;

  // counts[p] is the number of packs of size pack_sizes[p] bought
  vec<IntVar*> counts;
  vec<int> sizes;
  for (int p = 0; p < kinds; ++p) {
    counts.push(newIntVar(0, target));
    sizes.push(pack_sizes[p]);
  }

  // total is the number of items bought; a total above target plus the largest pack can never be optimal, so it bounds the domain
  IntVar* total = newIntVar(0, target + largest);
  int_linear(sizes, counts, IRT_EQ, total);

  // the items bought must meet or exceed the target
  int_linear(sizes, counts, IRT_GE, target);

  // minimize the number of items bought; branch on the pack counts in order
  branch(counts, VAR_INORDER, VAL_MIN);
  optimize(total, OPT_MIN);

  json out = json::array();
  for (int p = 0; p < kinds; ++p) out.push_back(dcp::out(counts[p]));
  outputs = {{"counts", out}};
}
