#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Schur's lemma: drop n balls into c boxes so that no box holds a triple
// x, y, z with x + y = z.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n = instance.at("n").get<int>();
  const int c = instance.at("c").get<int>();

  std::vector<IntVar> balls;
  for (int i = 0; i < n; ++i) balls.push_back(model.NewIntVar(Domain(1, c)));

  // Ball labels are 1-based, so ball k lives at balls[k - 1].  x and y may be
  // the same ball, in which case the first disjunct is simply unsatisfiable.
  for (int x = 1; x < n; ++x) {
    for (int y = 1; y <= n - x; ++y) {
      const int z = x + y;
      if (z > n) continue;
      BoolVar xy = model.NewBoolVar();
      BoolVar xz = model.NewBoolVar();
      BoolVar yz = model.NewBoolVar();
      model.AddNotEqual(balls[x - 1], balls[y - 1]).OnlyEnforceIf(xy);
      model.AddEquality(balls[x - 1], balls[y - 1]).OnlyEnforceIf(xy.Not());
      model.AddNotEqual(balls[x - 1], balls[z - 1]).OnlyEnforceIf(xz);
      model.AddEquality(balls[x - 1], balls[z - 1]).OnlyEnforceIf(xz.Not());
      model.AddNotEqual(balls[y - 1], balls[z - 1]).OnlyEnforceIf(yz);
      model.AddEquality(balls[y - 1], balls[z - 1]).OnlyEnforceIf(yz.Not());
      model.AddBoolOr({xy, xz, yz});
    }
  }

  json out = json::array();
  for (const IntVar& b : balls) out.push_back(b.index());
  outputs = {{"balls", out}};
}
