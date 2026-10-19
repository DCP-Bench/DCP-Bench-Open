#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const std::vector<int> npv = instance.at("npv").get<std::vector<int>>();
  const std::vector<int> cash_flow = instance.at("cash_flow").get<std::vector<int>>();
  const int budget = instance.at("budget").get<int>();
  const int n = static_cast<int>(npv.size());

  // each investment is either chosen (1) or not chosen (0)
  std::vector<dcp::Lin> x;
  for (int i = 0; i < n; ++i) x.push_back(dcp::new_var(h, 0, 1));

  // the total cash outflow of the chosen investments stays within the budget
  dcp::Lin spend;
  for (int i = 0; i < n; ++i) spend = spend + cash_flow[i] * x[i];
  dcp::add_row(h, spend, -kHighsInf, budget);

  // the total NPV is the sum of the NPVs of the chosen investments
  dcp::Lin z;
  for (int i = 0; i < n; ++i) z = z + npv[i] * x[i];

  out.add("x", x);
  out.add("z", z);
  out.maximize(z);
}
