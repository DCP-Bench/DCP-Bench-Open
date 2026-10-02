#include <algorithm>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Aircraft landing: choose a landing time for each aircraft on a single runway,
// inside its time window and with the required gap after each earlier landing,
// so that the penalty for landing before or after its target time is minimal.
// The landing order is fixed: aircraft i lands before aircraft j when i < j.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<int64_t> earliest_landing =
      instance.at("earliest_landing").get<std::vector<int64_t>>();
  const std::vector<int64_t> latest_landing =
      instance.at("latest_landing").get<std::vector<int64_t>>();
  const std::vector<int64_t> target_landing =
      instance.at("target_landing").get<std::vector<int64_t>>();
  const std::vector<int64_t> penalty_after =
      instance.at("penalty_after").get<std::vector<int64_t>>();
  const std::vector<int64_t> penalty_before =
      instance.at("penalty_before").get<std::vector<int64_t>>();
  const std::vector<std::vector<int64_t>> separation_time =
      instance.at("separation_time").get<std::vector<std::vector<int64_t>>>();
  const int num_aircraft = static_cast<int>(earliest_landing.size());

  // Time horizon: no landing is later than the largest latest-landing time.
  // The reference gives landing_times, earliness and lateness all this domain.
  const int64_t horizon =
      *std::max_element(latest_landing.begin(), latest_landing.end());

  std::vector<IntVar> landing_times, earliness, lateness;
  for (int i = 0; i < num_aircraft; ++i) {
    landing_times.push_back(model.NewIntVar(Domain(0, horizon)));
    earliness.push_back(model.NewIntVar(Domain(0, horizon)));
    lateness.push_back(model.NewIntVar(Domain(0, horizon)));
  }

  // Each aircraft lands inside its own time window.
  for (int i = 0; i < num_aircraft; ++i) {
    model.AddGreaterOrEqual(landing_times[i], earliest_landing[i]);
    model.AddLessOrEqual(landing_times[i], latest_landing[i]);
  }

  // The gap between the target and the actual landing time is earliness when
  // the aircraft lands before its target and lateness when it lands after.
  for (int i = 0; i < num_aircraft; ++i) {
    model.AddEquality(landing_times[i] - target_landing[i],
                      lateness[i] - earliness[i]);
  }

  // Separation: an aircraft that lands after another keeps at least the
  // separation time between the two (landing order i before j for i < j).
  for (int i = 0; i < num_aircraft; ++i) {
    for (int j = i + 1; j < num_aircraft; ++j) {
      model.AddGreaterOrEqual(landing_times[j] - landing_times[i],
                              separation_time[i][j]);
    }
  }

  // Total penalty: per-unit penalties for landing before and after the target.
  // Its upper bound follows from earliness and lateness being at most horizon.
  int64_t penalty_bound = 0;
  LinearExpr penalty;
  for (int i = 0; i < num_aircraft; ++i) {
    penalty += penalty_before[i] * earliness[i] + penalty_after[i] * lateness[i];
    penalty_bound += (penalty_before[i] + penalty_after[i]) * horizon;
  }
  IntVar total_penalty = model.NewIntVar(Domain(0, penalty_bound));
  model.AddEquality(total_penalty, penalty);
  model.Minimize(total_penalty);

  json times_out = json::array();
  for (const IntVar& v : landing_times) times_out.push_back(v.index());
  outputs = {{"landing_times", times_out},
             {"total_penalty", total_penalty.index()}};
}
