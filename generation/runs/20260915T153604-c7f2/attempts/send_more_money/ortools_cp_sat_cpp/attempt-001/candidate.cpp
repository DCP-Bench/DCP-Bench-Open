#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// SEND + MORE = MONEY: the classic alphametic.  The puzzle carries no instance
// data of its own, so every constant here is part of the puzzle statement.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  (void)instance;

  const Domain digit(0, 9);
  IntVar s = model.NewIntVar(digit);
  IntVar e = model.NewIntVar(digit);
  IntVar n = model.NewIntVar(digit);
  IntVar d = model.NewIntVar(digit);
  IntVar m = model.NewIntVar(digit);
  IntVar o = model.NewIntVar(digit);
  IntVar r = model.NewIntVar(digit);
  IntVar y = model.NewIntVar(digit);

  model.AddAllDifferent({s, e, n, d, m, o, r, y});

  const LinearExpr send = 1000 * s + 100 * e + 10 * n + d;
  const LinearExpr more = 1000 * m + 100 * o + 10 * r + e;
  const LinearExpr money = 10000 * m + 1000 * o + 100 * n + 10 * e + y;
  model.AddEquality(send + more, money);

  model.AddGreaterThan(s, 0);
  model.AddGreaterThan(m, 0);

  outputs = {{"s", s.index()}, {"e", e.index()}, {"n", n.index()},
             {"d", d.index()}, {"m", m.index()}, {"o", o.index()},
             {"r", r.index()}, {"y", y.index()}};
}
