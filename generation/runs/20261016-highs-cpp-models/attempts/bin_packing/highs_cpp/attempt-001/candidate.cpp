// Bin packing: assign each item to one bin so that the total weight in each bin
// does not exceed the bin capacity. Output: the bin of each item, 0-indexed.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const std::vector<int> weights = instance.at("weights").get<std::vector<int>>();
  const int capacity = instance.at("capacity").get<int>();
  const int num_bins = instance.at("num_bins").get<int>();
  const int n = static_cast<int>(weights.size());

  // x[i][b] = 1 if item i is put in bin b (bins are 0-indexed, 0..num_bins-1)
  std::vector<std::vector<dcp::Lin>> x(n, std::vector<dcp::Lin>(num_bins));
  for (int i = 0; i < n; ++i)
    for (int b = 0; b < num_bins; ++b) x[i][b] = dcp::new_var(h, 0, 1);

  // every item is in exactly one bin
  for (int i = 0; i < n; ++i) {
    dcp::Lin one_bin;
    for (int b = 0; b < num_bins; ++b) one_bin = one_bin + x[i][b];
    dcp::add_row(h, one_bin, 1, 1);
  }

  // the total weight of the items in each bin does not exceed the capacity
  for (int b = 0; b < num_bins; ++b) {
    dcp::Lin load;
    for (int i = 0; i < n; ++i) load = load + weights[i] * x[i][b];
    dcp::add_row(h, load, -kHighsInf, capacity);
  }

  // the bin of each item is the bin index whose indicator is 1
  std::vector<dcp::Lin> bins(n);
  for (int i = 0; i < n; ++i) {
    dcp::Lin index;
    for (int b = 0; b < num_bins; ++b) index = index + b * x[i][b];
    bins[i] = index;
  }
  out.add("bins", bins);
}
