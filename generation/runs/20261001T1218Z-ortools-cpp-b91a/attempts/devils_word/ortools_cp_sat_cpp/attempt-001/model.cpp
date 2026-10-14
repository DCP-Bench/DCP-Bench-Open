#include <algorithm>
#include <cstdlib>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Devil's word: put a '+' or a '-' in front of each integer of the array so
// that the signed numbers add up to the given total.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<int64_t> arr = instance.at("arr").get<std::vector<int64_t>>();
  const int64_t total = instance.at("total").get<int64_t>();
  const int n = static_cast<int>(arr.size());

  // A signed number lies between -max and max, where max is the largest
  // absolute value in the array.
  int64_t max_val = 0;
  for (const int64_t a : arr) max_val = std::max<int64_t>(max_val, std::llabs(a));

  // plus[i] is true when arr[i] is added and false when it is subtracted.
  std::vector<BoolVar> plus;
  // result[i] is arr[i] with its chosen sign.
  std::vector<IntVar> result;
  for (int i = 0; i < n; ++i) {
    plus.push_back(model.NewBoolVar());
    result.push_back(model.NewIntVar(Domain(-max_val, max_val)));
  }

  // Each number is either added or subtracted (a single Boolean carries both
  // choices), and result[i] holds the number with that sign.
  for (int i = 0; i < n; ++i) {
    // arr[i] * (2 * plus - 1) is +arr[i] when plus is true, -arr[i] otherwise.
    model.AddEquality(result[i], 2 * arr[i] * plus[i] - arr[i]);
  }

  // The signed numbers add up to the total.
  LinearExpr sum;
  for (int i = 0; i < n; ++i) sum += result[i];
  model.AddEquality(sum, total);

  json out = json::array();
  for (const IntVar& v : result) out.push_back(v.index());
  outputs = {{"result", out}};
}
