#include <algorithm>
#include <vector>

#include "dcp.h"

// Aircraft land on one runway in the index order of the instance (the fixed landing sequence).
// Each aircraft i lands at an integer time x_i within its own earliest and latest landing times.
// Landing earlier than its target time costs penalty_before, landing later costs penalty_after.
// Consecutive aircraft need at least the separation time between them, and every later aircraft
// also needs its separation from every earlier one.
void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const auto earliest = instance.at("earliest_landing").get<std::vector<int>>();
  const auto latest = instance.at("latest_landing").get<std::vector<int>>();
  const auto target = instance.at("target_landing").get<std::vector<int>>();
  const auto penalty_before = instance.at("penalty_before").get<std::vector<int>>();
  const auto penalty_after = instance.at("penalty_after").get<std::vector<int>>();
  const auto separation = instance.at("separation_time").get<std::vector<std::vector<int>>>();
  const int n = static_cast<int>(earliest.size());

  // Landing time of each aircraft, inside its time window.
  std::vector<dcp::Lin> x;
  for (int i = 0; i < n; ++i) x.push_back(dcp::new_var(h, earliest[i], latest[i]));

  // Earliness and lateness of each aircraft against its target. The amounts are bounded by the
  // data: the distance from the target to the window's end on that side.
  std::vector<dcp::Lin> early, late;
  for (int i = 0; i < n; ++i) {
    early.push_back(dcp::new_var(h, 0, std::max(0, target[i] - earliest[i])));
    late.push_back(dcp::new_var(h, 0, std::max(0, latest[i] - target[i])));
  }

  // early_i is at least target_i - x_i: early_i + x_i >= target_i.
  for (int i = 0; i < n; ++i) dcp::add_row(h, early[i] + x[i], target[i], kHighsInf);
  // late_i is at least x_i - target_i: late_i - x_i >= -target_i.
  for (int i = 0; i < n; ++i) dcp::add_row(h, late[i] - x[i], -target[i], kHighsInf);

  // Separation: a later aircraft j lands at least separation_time(i, j) after an earlier aircraft i.
  for (int i = 0; i < n; ++i)
    for (int j = i + 1; j < n; ++j) dcp::add_row(h, x[j] - x[i], separation[i][j], kHighsInf);

  // Total penalty: each aircraft pays its earliness and lateness penalties.
  dcp::Lin total_penalty;
  for (int i = 0; i < n; ++i)
    total_penalty = total_penalty + penalty_before[i] * early[i] + penalty_after[i] * late[i];

  out.add("landing_times", x);
  out.add("total_penalty", total_penalty);
  out.minimize(total_penalty);
}
