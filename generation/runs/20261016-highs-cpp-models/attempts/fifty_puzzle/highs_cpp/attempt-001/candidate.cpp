// Fifty puzzle (Loyd's dummies): choose a set of dummies whose numbers add up
// to exactly the target sum; output which dummies are knocked over.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  // the numbers on the dummies, one per dummy, and the target sum (from the instance)
  std::vector<int> values = instance.at("values").get<std::vector<int>>();
  int target_sum = instance.at("target_sum").get<int>();
  int n = static_cast<int>(values.size());

  // dummies[i] = 1 if dummy i is knocked over (a binary per dummy)
  std::vector<dcp::Lin> dummies;
  for (int i = 0; i < n; i++) {
    dummies.push_back(dcp::new_var(h, 0, 1, true));
  }

  // the sum of the numbers on the knocked-over dummies equals the target sum exactly
  dcp::Lin total = 0;
  for (int i = 0; i < n; i++) {
    total = total + static_cast<double>(values[i]) * dummies[i];
  }
  dcp::add_row(h, total, target_sum, target_sum);

  out.add("dummies", dummies);
}
