#include "dcp.h"

// csplib_022 bus driver scheduling: choose a set of shifts so that every piece of
// work is covered by exactly one chosen shift, and minimise the number of shifts chosen.

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const int num_work = instance.at("num_work").get<int>();
  const json& shifts = instance.at("shifts");
  const int num_shifts = static_cast<int>(shifts.size());

  // x[s] = 1 when shift s is selected
  std::vector<dcp::Lin> x;
  for (int s = 0; s < num_shifts; ++s) x.push_back(dcp::new_var(h, 0, 1));

  // shifts covering each piece of work (0-based task indices in the data)
  std::vector<std::vector<int>> covering_shifts(num_work);
  for (int s = 0; s < num_shifts; ++s)
    for (const json& task : shifts[s])
      covering_shifts[task.get<int>()].push_back(s);

  // every piece of work is covered by exactly one selected shift
  for (int w = 0; w < num_work; ++w) {
    dcp::Lin cover;
    for (int s : covering_shifts[w]) cover = cover + x[s];
    dcp::add_row(h, cover, 1, 1);
  }

  // the number of selected shifts is minimised
  dcp::Lin total;
  for (int s = 0; s < num_shifts; ++s) total = total + x[s];
  out.minimize(total);

  // output: the selection vector, one entry per shift
  out.add("x", x);
}
