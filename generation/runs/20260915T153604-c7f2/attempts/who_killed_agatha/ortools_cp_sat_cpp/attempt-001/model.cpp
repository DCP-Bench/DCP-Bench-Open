#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Who killed Agatha: three residents of Dreadsbury Mansion, a web of hatred
// and wealth, and exactly one consistent culprit.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<std::string> names =
      instance.at("names").get<std::vector<std::string>>();
  const int n = static_cast<int>(names.size());

  // The roles are positional in the puzzle statement: the names list runs
  // Agatha, the butler, Charles, and Agatha is the victim.
  const int agatha = 0;
  const int butler = 1;
  const int charles = 2;
  const int victim = agatha;

  IntVar killer = model.NewIntVar(Domain(0, n - 1));

  std::vector<std::vector<BoolVar>> hates(n);
  std::vector<std::vector<BoolVar>> richer(n);
  for (int i = 0; i < n; ++i) {
    for (int j = 0; j < n; ++j) {
      hates[i].push_back(model.NewBoolVar());
      richer[i].push_back(model.NewBoolVar());
    }
  }

  // A killer always hates, and is no richer than, the victim.  The killer is a
  // variable, so both facts are read off with an element constraint.
  std::vector<LinearExpr> hates_victim;
  std::vector<LinearExpr> richer_than_victim;
  for (int i = 0; i < n; ++i) {
    hates_victim.push_back(hates[i][victim]);
    richer_than_victim.push_back(richer[i][victim]);
  }
  IntVar killer_hates_victim = model.NewIntVar(Domain(0, 1));
  IntVar killer_richer_victim = model.NewIntVar(Domain(0, 1));
  model.AddElement(killer, hates_victim, killer_hates_victim);
  model.AddElement(killer, richer_than_victim, killer_richer_victim);
  model.AddEquality(killer_hates_victim, 1);
  model.AddEquality(killer_richer_victim, 0);

  // Nobody is richer than himself, and richer is antisymmetric and total.
  for (int i = 0; i < n; ++i) model.AddEquality(richer[i][i], 0);
  for (int i = 0; i < n; ++i) {
    for (int j = i + 1; j < n; ++j) {
      model.AddNotEqual(richer[i][j], richer[j][i]);
    }
  }

  // Charles hates nobody that Agatha hates.
  for (int i = 0; i < n; ++i) {
    model.AddImplication(hates[agatha][i], hates[charles][i].Not());
  }

  // Agatha hates everybody except the butler.
  model.AddEquality(hates[agatha][agatha], 1);
  model.AddEquality(hates[agatha][charles], 1);
  model.AddEquality(hates[agatha][butler], 0);

  // The butler hates everyone not richer than Agatha, and everyone Agatha
  // hates.
  for (int i = 0; i < n; ++i) {
    model.AddImplication(richer[i][agatha].Not(), hates[butler][i]);
    model.AddImplication(hates[agatha][i], hates[butler][i]);
  }

  // Nobody hates everyone.
  for (int i = 0; i < n; ++i) {
    LinearExpr hated;
    for (int j = 0; j < n; ++j) hated += hates[i][j];
    model.AddLessOrEqual(hated, n - 1);
  }

  outputs = {{"killer", killer.index()}};
}
