#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"
using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  int n = instance.at("n");
  auto x = model.NewIntVar(Domain(0, n));
  auto y = model.NewIntVar(Domain(0, n));
  if (instance.at("optimize").get<bool>()) {
    model.AddGreaterOrEqual(x + y, n);
    model.Minimize(x + y);
  } else {
    model.AddEquality(x + y, n);
  }
  outputs = {{"x", x.index()}, {"y", y.index()}};
}
