#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Airline crew rostering: staff every flight with the right size and skill
// mix, and give anyone who flies a break of two flights afterwards.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<std::vector<int64_t>> attributes =
      instance.at("attributes").get<std::vector<std::vector<int64_t>>>();
  const std::vector<std::vector<int64_t>> required_crew =
      instance.at("required_crew").get<std::vector<std::vector<int64_t>>>();
  const int num_persons = static_cast<int>(attributes.size());
  const int num_flights = static_cast<int>(required_crew.size());
  // The attribute columns are steward, hostess, french, spanish, german; the
  // requirement row is crew size followed by those same five counts.
  const int num_attributes =
      num_persons == 0 ? 0 : static_cast<int>(attributes[0].size());

  std::vector<std::vector<BoolVar>> crew(num_flights);
  for (int f = 0; f < num_flights; ++f) {
    for (int p = 0; p < num_persons; ++p) crew[f].push_back(model.NewBoolVar());
  }

  // The reference counts the people who fly at least once and pins that count
  // to a variable with a domain starting at one, so at least one person flies.
  LinearExpr flying;
  for (int p = 0; p < num_persons; ++p) {
    BoolVar works = model.NewBoolVar();
    std::vector<BoolVar> flights_of_p;
    for (int f = 0; f < num_flights; ++f) flights_of_p.push_back(crew[f][p]);
    model.AddBoolOr(flights_of_p).OnlyEnforceIf(works);
    for (int f = 0; f < num_flights; ++f) {
      model.AddImplication(crew[f][p], works);
    }
    flying += works;
  }
  IntVar num_working = model.NewIntVar(Domain(1, num_persons));
  model.AddEquality(num_working, flying);

  for (int f = 0; f < num_flights; ++f) {
    LinearExpr size;
    for (int p = 0; p < num_persons; ++p) size += crew[f][p];
    model.AddEquality(size, required_crew[f][0]);

    for (int j = 0; j < num_attributes; ++j) {
      LinearExpr skilled;
      for (int p = 0; p < num_persons; ++p) {
        skilled += attributes[p][j] * crew[f][p];
      }
      model.AddGreaterOrEqual(skilled, required_crew[f][j + 1]);
    }
  }

  // After a flight, two flights off.
  for (int f = 0; f + 2 < num_flights; ++f) {
    for (int p = 0; p < num_persons; ++p) {
      model.AddLessOrEqual(crew[f][p] + crew[f + 1][p] + crew[f + 2][p], 1);
    }
  }

  json out = json::array();
  for (int f = 0; f < num_flights; ++f) {
    json row = json::array();
    for (int p = 0; p < num_persons; ++p) row.push_back(crew[f][p].index());
    out.push_back(row);
  }
  outputs = {{"crew", out}};
}
