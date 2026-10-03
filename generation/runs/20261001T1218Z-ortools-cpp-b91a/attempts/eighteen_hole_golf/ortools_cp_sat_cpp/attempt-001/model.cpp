#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// 18-hole golf: lay out an 18-hole course where every hole has length 3, 4 or
// 5 and the whole course has length 72.
// The problem has no instance data; the hole count, the allowed lengths and
// the total all come from the statement.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  const int num_holes = 18;
  const int total_length = 72;

  // Each hole has a length of 3, 4 or 5.
  std::vector<IntVar> holes;
  LinearExpr course;
  for (int i = 0; i < num_holes; ++i) {
    holes.push_back(model.NewIntVar(Domain(3, 5)));
    course += holes.back();
  }

  // The total length of the course is 72.
  model.AddEquality(course, total_length);

  json leaves = json::array();
  for (const IntVar& hole : holes) leaves.push_back(hole.index());
  outputs = {{"holes", leaves}};
}
