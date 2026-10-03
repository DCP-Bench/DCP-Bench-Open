#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Joyner's five statements: statement i (1..5) says "exactly i of these
// statements are false". Decide which statements are true.
// The problem has no instance data.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  const int count = 5;
  std::vector<BoolVar> statements;
  LinearExpr false_count;  // number of false statements
  for (int i = 0; i < count; ++i) {
    statements.push_back(model.NewBoolVar());
    false_count += statements.back().Not();  // the negated literal counts 1 when false
  }

  // Statement i is true exactly when i+1 of the statements are false.
  for (int i = 0; i < count; ++i) {
    model.AddEquality(false_count, i + 1).OnlyEnforceIf(statements[i]);
    model.AddNotEqual(false_count, i + 1).OnlyEnforceIf(statements[i].Not());
  }

  json leaves = json::array();
  for (const BoolVar& statement : statements) leaves.push_back(statement.index());
  outputs = {{"statements", leaves}};
}
