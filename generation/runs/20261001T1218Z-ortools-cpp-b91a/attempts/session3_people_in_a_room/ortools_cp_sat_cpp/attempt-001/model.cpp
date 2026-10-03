#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// People in a room: 13 people, 4 of them male, enter a room one at a time.
// Find an order of males and females such that the ratio of females to males
// in the room never exceeds 7/3.
// The problem has no instance data; 13 and 4 come from the statement.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  const int total_people = 13;
  const int num_males = 4;

  // sequence[i] is 1 if the i-th person to enter is female, 0 if male.
  std::vector<BoolVar> sequence;
  LinearExpr females;
  for (int i = 0; i < total_people; ++i) {
    sequence.push_back(model.NewBoolVar());
    females += sequence.back();
  }

  // Exactly 13 - 4 = 9 of the people are female.
  model.AddEquality(females, total_people - num_males);

  // After each of the first i entries (i = 1..12), females/males <= 7/3, stated
  // without division as 3 * females <= 7 * males, with males = i - females.
  for (int i = 1; i < total_people; ++i) {
    LinearExpr females_so_far;
    for (int k = 0; k < i; ++k) females_so_far += sequence[k];
    model.AddLessOrEqual(3 * females_so_far, 7 * (i - females_so_far));
  }

  json leaves = json::array();
  for (const BoolVar& person : sequence) leaves.push_back(person.index());
  outputs = {{"sequence", leaves}};
}
