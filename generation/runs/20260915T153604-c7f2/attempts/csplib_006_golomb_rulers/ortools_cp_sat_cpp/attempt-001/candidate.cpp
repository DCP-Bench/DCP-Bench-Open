#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Golomb ruler: increasing marks starting at zero whose pairwise differences
// are all distinct, as short as possible.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int size = instance.at("size").get<int>();

  // Mark positions run 0..size^2, the reference's declared bound.
  std::vector<IntVar> marks;
  for (int i = 0; i < size; ++i) {
    marks.push_back(model.NewIntVar(Domain(0, int64_t{size} * size)));
  }

  model.AddEquality(marks[0], 0);
  for (int i = 0; i + 1 < size; ++i) {
    model.AddLessThan(marks[i], marks[i + 1]);
  }

  std::vector<LinearExpr> diffs;
  for (int i = 0; i + 1 < size; ++i) {
    for (int j = i + 1; j < size; ++j) diffs.push_back(marks[j] - marks[i]);
  }
  model.AddAllDifferent(diffs);

  // The ruler's length is its last mark.
  IntVar length = marks[size - 1];
  model.Minimize(length);

  json marks_out = json::array();
  for (const IntVar& m : marks) marks_out.push_back(m.index());
  outputs = {{"marks", marks_out}, {"length", length.index()}};
}
