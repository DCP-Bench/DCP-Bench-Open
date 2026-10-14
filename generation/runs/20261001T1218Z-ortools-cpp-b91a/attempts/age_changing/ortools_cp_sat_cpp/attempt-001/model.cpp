#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Age changing (Enigma 1224): applying the four operations +2, /8, -3 and *7
// in some order to my age gives my husband's age, and applying them in a
// different order to his age gives mine. What are our two ages?
// The problem has no instance data: the operations and the age range 16..120
// are part of the puzzle; intermediate results are kept in 1..1000.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  const int n = 4;  // number of operations: 0 = +2, 1 = /8, 2 = -3, 3 = *7
  const IntVar m = model.NewIntVar(Domain(16, 120));  // my age
  const IntVar h = model.NewIntVar(Domain(16, 120));  // husband's age

  // order[i][k] is true when operation k is applied as step i; perm[i] is the
  // number of that operation. Each sequence uses every operation once.
  auto sequence = [&](std::vector<IntVar>& perm, std::vector<std::vector<BoolVar>>& order) {
    order.assign(n, {});
    for (int i = 0; i < n; ++i) {
      LinearExpr chosen;
      for (int k = 0; k < n; ++k) {
        order[i].push_back(model.NewBoolVar());
        chosen += k * order[i][k];
      }
      model.AddExactlyOne(order[i]);
      const IntVar p = model.NewIntVar(Domain(0, n - 1));
      model.AddEquality(p, chosen);
      perm.push_back(p);
    }
    model.AddAllDifferent(perm);
  };
  std::vector<IntVar> perm1, perm2;
  std::vector<std::vector<BoolVar>> order1, order2;
  sequence(perm1, order1);
  sequence(perm2, order2);

  // The two orders differ in at least one step.
  std::vector<BoolVar> differs;
  for (int i = 0; i < n; ++i) {
    const BoolVar d = model.NewBoolVar();
    model.AddNotEqual(perm1[i], perm2[i]).OnlyEnforceIf(d);
    differs.push_back(d);
  }
  model.AddBoolOr(differs);

  // Applying step i turns value old into value next. Division by 8 is stated
  // as 8 * next == old, so it is only possible when old is a multiple of 8.
  auto apply = [&](const std::vector<BoolVar>& op, const IntVar& old, const IntVar& next) {
    model.AddEquality(next, old + 2).OnlyEnforceIf(op[0]);
    model.AddEquality(8 * next, old).OnlyEnforceIf(op[1]);
    model.AddEquality(next, old - 3).OnlyEnforceIf(op[2]);
    model.AddEquality(next, 7 * old).OnlyEnforceIf(op[3]);
  };

  // hlist starts from my age and ends at my husband's age; mlist starts from
  // his age and ends at mine.
  std::vector<IntVar> hlist, mlist;
  for (int i = 0; i <= n; ++i) {
    hlist.push_back(model.NewIntVar(Domain(1, 1000)));
    mlist.push_back(model.NewIntVar(Domain(1, 1000)));
  }
  model.AddEquality(hlist[0], m);
  model.AddEquality(h, hlist[n]);
  model.AddEquality(mlist[0], h);
  model.AddEquality(m, mlist[n]);
  for (int i = 0; i < n; ++i) {
    apply(order1[i], hlist[i], hlist[i + 1]);
    apply(order2[i], mlist[i], mlist[i + 1]);
  }

  outputs = {{"m", m.index()}, {"h", h.index()}};
}
