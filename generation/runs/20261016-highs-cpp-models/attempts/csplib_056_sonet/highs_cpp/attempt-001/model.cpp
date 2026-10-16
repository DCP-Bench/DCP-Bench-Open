// SONET problem (CSPLib 056): place nodes on rings so that every demand pair shares
// a ring, each ring holds at most its capacity of nodes, and the total number of
// add-drop multiplexers (ADMs) is minimised.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const int r = instance.at("r").get<int>();
  const int n = instance.at("n").get<int>();
  const std::vector<int> capacity = instance.at("capacity_nodes").get<std::vector<int>>();
  const json& demand = instance.at("demand");

  // on[k][i] = 1 if node i is installed on ring k
  std::vector<std::vector<dcp::Lin>> on(r, std::vector<dcp::Lin>(n));
  for (int k = 0; k < r; ++k)
    for (int i = 0; i < n; ++i) on[k][i] = dcp::new_var(h, 0, 1);

  // a ring hosts at most as many nodes as its capacity
  for (int k = 0; k < r; ++k) {
    // the number of nodes on ring k is at most its capacity
    dcp::Lin count;
    for (int i = 0; i < n; ++i) count = count + on[k][i];
    dcp::add_row(h, count, -kHighsInf, capacity[k]);
  }

  // every pair of nodes with a traffic demand (in either direction) must share a ring
  for (int i = 0; i < n; ++i) {
    for (int j = i + 1; j < n; ++j) {
      if (demand[i][j].get<int>() == 0 && demand[j][i].get<int>() == 0) continue;
      // both nodes are on a common ring: together[k] = 1 means ring k carries both
      dcp::Lin any_common;
      for (int k = 0; k < r; ++k) {
        dcp::Lin together = dcp::new_var(h, 0, 1);
        // together = 1 implies node i is on ring k
        dcp::add_row(h, together - on[k][i], -kHighsInf, 0);
        // together = 1 implies node j is on ring k
        dcp::add_row(h, together - on[k][j], -kHighsInf, 0);
        any_common = any_common + together;
      }
      // at least one ring carries both nodes of the demand pair
      dcp::add_row(h, any_common, 1, kHighsInf);
    }
  }

  // total ADMs: one per node installed on a ring
  dcp::Lin total_adms;
  for (int k = 0; k < r; ++k)
    for (int i = 0; i < n; ++i) total_adms = total_adms + on[k][i];
  out.minimize(total_adms);

  out.add("ring_config", on);
  out.add("total_adms", total_adms);
}
