#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Handshaking: Hilary and Jocelyn (a couple) host num_couples other couples.
// Everybody shakes hands with some of the others, never with themselves or
// their spouse. Everybody except Hilary reports a different number of
// handshakes. Find how many hands Hilary shook.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int num_couples = instance.at("num_couples").get<int>();
  // Persons are numbered so that couples are neighbours: (0,1), (2,3), ...
  // Hilary is person 0 and Jocelyn is person 1.
  const int n = 2 + num_couples * 2;

  // x[i] is the number of hands person i has shaken; at most n - 2, since
  // nobody shakes with themselves or their spouse.
  std::vector<IntVar> x;
  for (int i = 0; i < n; ++i) x.push_back(model.NewIntVar(Domain(0, n - 2)));

  // y[i][j] is true when person i shakes hands with person j.
  std::vector<std::vector<BoolVar>> y(n);
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j) y[i].push_back(model.NewBoolVar());

  // The answers of everybody except Hilary are all different.
  model.AddAllDifferent(std::vector<IntVar>(x.begin() + 1, x.end()));

  // Nobody shakes hands with their spouse.
  for (int i = 0; i < n / 2; ++i) {
    model.AddEquality(y[2 * i][2 * i + 1], 0);
    model.AddEquality(y[2 * i + 1][2 * i], 0);
  }

  for (int i = 0; i < n; ++i) {
    // Nobody shakes hands with themselves.
    model.AddEquality(y[i][i], 0);
    // x[i] counts the hands person i has shaken.
    LinearExpr shaken;
    for (int j = 0; j < n; ++j) shaken += y[i][j];
    model.AddEquality(x[i], shaken);
  }

  // Handshaking is mutual: i shakes hands with j exactly when j shakes with i.
  for (int i = 0; i < n; ++i)
    for (int j = i + 1; j < n; ++j) model.AddEquality(y[i][j], y[j][i]);

  // hil is the number of hands Hilary (person 0) has shaken.
  outputs = {{"hil", x[0].index()}};
}
