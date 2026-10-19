// Three sum: given a collection of integers, select a number m of elements whose
// values sum to zero. indices[i] is 1 when element i is selected.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  // the collection of integers, and the number of elements to select
  std::vector<int> nums = instance.at("nums").get<std::vector<int>>();
  int m = instance.at("m");
  int n = static_cast<int>(nums.size());

  // indices[i] = 1 if element i is selected (binary column per element)
  std::vector<dcp::Lin> indices;
  for (int i = 0; i < n; ++i) indices.push_back(dcp::new_var(h, 0, 1));

  // exactly m elements are selected
  dcp::Lin count;
  for (int i = 0; i < n; ++i) count = count + indices[i];
  dcp::add_row(h, count, m, m);

  // the selected elements sum to zero
  dcp::Lin total;
  for (int i = 0; i < n; ++i) total = total + static_cast<double>(nums[i]) * indices[i];
  dcp::add_row(h, total, 0, 0);

  out.add("indices", indices);
}
