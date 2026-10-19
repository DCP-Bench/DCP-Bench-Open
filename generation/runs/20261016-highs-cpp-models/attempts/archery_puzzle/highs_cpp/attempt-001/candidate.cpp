// Archery puzzle: the archer shoots as many arrows as she likes. An arrow on target i
// scores targets[i]. The total should come as close as possible to target_score, so
// the deviation |total - target_score| is minimised. hits[i] counts the arrows on target i.
#include <cmath>
#include <stdexcept>

#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  std::vector<double> targets;
  for (const auto& v : instance.at("targets")) targets.push_back(v.get<double>());
  const double target = instance.at("target_score").get<double>();
  const double abs_target = std::fabs(target);

  // With no arrows the deviation is |target|, so an optimal total lies in
  // target - |target| .. target + |target|, that is at most 2 |target|. Every ring
  // scores a positive amount, so each hit count is at most 2 |target| / score.
  // Only non-optimal totals are cut off by these bounds.
  std::vector<dcp::Lin> hits;
  for (double score : targets) {
    if (score <= 0) throw std::runtime_error("ring scores must be positive");
    hits.push_back(dcp::new_var(h, 0, std::floor(2 * abs_target / score)));
  }

  // total = sum over the targets of score_i * hits_i
  dcp::Lin total(0.0);
  for (size_t i = 0; i < targets.size(); ++i) total = total + targets[i] * hits[i];

  // The deviation is never more than |target| in an optimal solution.
  dcp::Lin deviation = dcp::new_var(h, 0, abs_target);

  // deviation is at least total - target
  dcp::add_row(h, deviation - total, -target, kHighsInf);
  // deviation is at least target - total
  dcp::add_row(h, deviation + total, target, kHighsInf);

  out.add("hits", hits);
  out.minimize(deviation);
}
