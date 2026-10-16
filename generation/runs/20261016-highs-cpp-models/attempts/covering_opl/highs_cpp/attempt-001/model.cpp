#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int nb_workers = instance.at("nb_workers").get<int>();
  int num_tasks = instance.at("num_tasks").get<int>();
  const json& cost = instance.at("Cost");
  const json& qualified = instance.at("Qualified");

  // one hire flag per worker: 1 means the worker is selected
  std::vector<dcp::Lin> hired;
  for (int w = 0; w < nb_workers; ++w) hired.push_back(dcp::new_var(h, 0, 1));

  // every task is performed by at least one selected worker qualified for it
  for (int t = 0; t < num_tasks; ++t) {
    dcp::Lin covered = 0;
    for (const json& wj : qualified.at(t)) {
      int w = wj.get<int>() - 1; // data is 1-based
      covered = covered + hired[w];
    }
    dcp::add_row(h, covered, 1, kHighsInf);
  }

  // total hiring cost of the selected workers
  dcp::Lin total = 0;
  for (int w = 0; w < nb_workers; ++w)
    total = total + cost.at(w).get<double>() * hired[w];

  out.add("total_cost", total);
  out.add("workers", hired);
  out.minimize(total);
}
