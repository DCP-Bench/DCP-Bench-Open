// Contracting costs: find what each of six tradesmen charges, given the total payment for each pair of trades that work together.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // the six charges in dollars are the unknowns; each is at most the largest pair total (5300)
  IntVar* paper_hanger = newIntVar(0, 10000);
  IntVar* painter = newIntVar(0, 10000);
  IntVar* plumber = newIntVar(0, 10000);
  IntVar* electrician = newIntVar(0, 10000);
  IntVar* carpenter = newIntVar(0, 10000);
  IntVar* mason = newIntVar(0, 10000);

  vec<int> ones;
  for (int i = 0; i < 2; ++i) ones.push(1);

  // the paper hanger and the painter together are paid $1,100
  {
    vec<IntVar*> p; p.push(paper_hanger); p.push(painter);
    int_linear(ones, p, IRT_EQ, 1100);
  }
  // the painter and the plumber together are paid $1,700
  {
    vec<IntVar*> p; p.push(painter); p.push(plumber);
    int_linear(ones, p, IRT_EQ, 1700);
  }
  // the plumber and the electrician together are paid $1,100
  {
    vec<IntVar*> p; p.push(plumber); p.push(electrician);
    int_linear(ones, p, IRT_EQ, 1100);
  }
  // the electrician and the carpenter together are paid $3,300
  {
    vec<IntVar*> p; p.push(electrician); p.push(carpenter);
    int_linear(ones, p, IRT_EQ, 3300);
  }
  // the carpenter and the mason together are paid $5,300
  {
    vec<IntVar*> p; p.push(carpenter); p.push(mason);
    int_linear(ones, p, IRT_EQ, 5300);
  }
  // the mason and the painter together are paid $3,200
  {
    vec<IntVar*> p; p.push(mason); p.push(painter);
    int_linear(ones, p, IRT_EQ, 3200);
  }

  // the six equations determine every charge from the painter's charge, so branch on that
  vec<IntVar*> decision;
  decision.push(painter);
  branch(decision, VAR_INORDER, VAL_MIN);

  outputs = {
    {"paper_hanger", dcp::out(paper_hanger)},
    {"painter", dcp::out(painter)},
    {"plumber", dcp::out(plumber)},
    {"electrician", dcp::out(electrician)},
    {"carpenter", dcp::out(carpenter)},
    {"mason", dcp::out(mason)}
  };
}
