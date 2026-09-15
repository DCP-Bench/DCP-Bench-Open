#include <numeric>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Capital budgeting: choose investments whose combined cash outflow fits the
// budget, maximizing total net present value.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<int64_t> npv =
      instance.at("npv").get<std::vector<int64_t>>();
  const std::vector<int64_t> cash_flow =
      instance.at("cash_flow").get<std::vector<int64_t>>();
  const int64_t budget = instance.at("budget").get<int64_t>();
  const int n = static_cast<int>(npv.size());

  std::vector<BoolVar> x;
  x.reserve(n);
  for (int i = 0; i < n; ++i) x.push_back(model.NewBoolVar());

  const int64_t npv_total = std::accumulate(npv.begin(), npv.end(), int64_t{0});
  IntVar z = model.NewIntVar(Domain(0, npv_total));

  LinearExpr outflow;
  LinearExpr value;
  for (int i = 0; i < n; ++i) {
    outflow += cash_flow[i] * x[i];
    value += npv[i] * x[i];
  }
  model.AddLessOrEqual(outflow, budget);
  model.AddEquality(z, value);
  model.Maximize(z);

  json x_out = json::array();
  for (const BoolVar& b : x) x_out.push_back(b.index());
  outputs = {{"z", z.index()}, {"x", x_out}};
}
