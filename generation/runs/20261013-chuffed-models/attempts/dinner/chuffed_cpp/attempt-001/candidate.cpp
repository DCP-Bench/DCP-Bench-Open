// Dinner: choose how many grandparents, parents and children go to dinner so that 20 people pay exactly $20.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // grandparents (1 to 6), parents (1 to 10) and children (1 to 40) are the unknowns; the problem fixes these ranges

  // grandparents[0] is the count of grandparents going to dinner
  IntVar* grandparents = newIntVar(1, 6);
  IntVar* parents = newIntVar(1, 10);
  IntVar* children = newIntVar(1, 40);

  vec<IntVar*> people;
  people.push(grandparents); people.push(parents); people.push(children);

  // there must be 20 people in total
  vec<int> ones;
  ones.push(1); ones.push(1); ones.push(1);
  int_linear(ones, people, IRT_EQ, 20);

  // the bill is $20, so in cents: grandparents pay 300, parents 200 and children 50
  vec<int> cents;
  cents.push(300); cents.push(200); cents.push(50);
  int_linear(cents, people, IRT_EQ, 2000);

  // the number of grandparents is the decision that fixes the rest; branch on it first
  vec<IntVar*> decision;
  decision.push(grandparents); decision.push(parents);
  branch(decision, VAR_INORDER, VAL_MIN);

  outputs = {
    {"grandparents", dcp::out(grandparents)},
    {"parents", dcp::out(parents)},
    {"children", dcp::out(children)}
  };
}
