#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Guards and apples: at each gate the boy hands over half his apples plus one,
// and walks away from the last gate with exactly one apple left.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int num_gates = instance.at("num_gates").get<int>();

  // Apple count domain 0..100 is the reference's declared bound.
  std::vector<IntVar> apples;
  for (int i = 0; i <= num_gates; ++i) {
    apples.push_back(model.NewIntVar(Domain(0, 100)));
  }

  model.AddEquality(apples[num_gates], 1);
  for (int i = 1; i <= num_gates; ++i) {
    model.AddEquality(apples[i - 1], 2 * (apples[i] + 1));
  }

  json out = json::array();
  for (const IntVar& a : apples) out.push_back(a.index());
  outputs = {{"apples", out}};
}
