#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Car sequencing: order the cars on an assembly line so that no station that
// installs an option is asked to handle more cars than its capacity allows
// within any window of consecutive slots.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<int64_t> at_most =
      instance.at("at_most").get<std::vector<int64_t>>();
  const std::vector<int64_t> per_slots =
      instance.at("per_slots").get<std::vector<int64_t>>();
  const std::vector<int64_t> demand =
      instance.at("demand").get<std::vector<int64_t>>();
  const std::vector<std::vector<int64_t>> requires_option =
      instance.at("requires").get<std::vector<std::vector<int64_t>>>();

  int64_t total_cars = 0;
  for (const int64_t d : demand) total_cars += d;
  const int n_cars = static_cast<int>(total_cars);  // cars to sequence
  const int n_options = static_cast<int>(at_most.size());
  const int n_types = static_cast<int>(demand.size());

  // sequence[s] is the car type placed in slot s (types start from 0).
  // is_type[s][t] is true exactly when slot s holds a car of type t; it is the
  // 0/1 form of sequence[s], so counting and the option windows stay linear.
  std::vector<IntVar> sequence;
  std::vector<std::vector<BoolVar>> is_type(n_cars);
  for (int s = 0; s < n_cars; ++s) {
    sequence.push_back(model.NewIntVar(Domain(0, n_types - 1)));
    LinearExpr one_type;
    LinearExpr type_value;
    for (int t = 0; t < n_types; ++t) {
      is_type[s].push_back(model.NewBoolVar());
      one_type += is_type[s][t];
      type_value += t * is_type[s][t];
    }
    // Every slot holds exactly one type, and that type is sequence[s].
    model.AddEquality(one_type, 1);
    model.AddEquality(sequence[s], type_value);
  }

  // The amount of each type of car in the sequence has to equal its demand.
  for (int t = 0; t < n_types; ++t) {
    LinearExpr count;
    for (int s = 0; s < n_cars; ++s) count += is_type[s][t];
    model.AddEquality(count, demand[t]);
  }

  // No more than at_most[o] cars needing option o in any window of per_slots[o]
  // consecutive slots.  Only complete windows are checked, as in the reference.
  // The number of cars in slot s that need option o is the sum of is_type[s][t]
  // over the types that require o.
  for (int o = 0; o < n_options; ++o) {
    for (int start = 0; start + per_slots[o] <= n_cars; ++start) {
      LinearExpr needing_option;
      for (int s = start; s < start + per_slots[o]; ++s) {
        for (int t = 0; t < n_types; ++t) {
          if (requires_option[t][o] != 0) {
            needing_option += requires_option[t][o] * is_type[s][t];
          }
        }
      }
      model.AddLessOrEqual(needing_option, at_most[o]);
    }
  }

  json out = json::array();
  for (const IntVar& v : sequence) out.push_back(v.index());
  outputs = {{"sequence", out}};
}
