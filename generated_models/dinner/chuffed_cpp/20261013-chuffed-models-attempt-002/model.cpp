// Dinner: choose how many grandparents, parents and children go to dinner so that 20 people pay exactly $20.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // the problem fixes the ranges: 1 to 6 grandparents, 1 to 10 parents, 1 to 40 children

  IntVar* grandparents = newIntVar(1, 6);
  IntVar* parents = newIntVar(1, 10);
  IntVar* children = newIntVar(1, 40);

  vec<IntVar*> people;
  people.push(grandparents); people.push(parents); people.push(children);

  // there must be 20 people at dinner in total
  vec<int> ones;
  ones.push(1); ones.push(1); ones.push(1);
  int_linear(ones, people, IRT_EQ, 20);

  // the dinner must cost $20; in cents a grandparent pays 300, a parent 200 and a child 50, so the total is 2000 cents
  vec<int> cents;
  cents.push(300); cents.push(200); cents.push(50);
  int_linear(cents, people, IRT_EQ, 2000);

  // the number of grandparents and parents fixes the number of children; branch on those first
  vec<IntVar*> decision;
  decision.push(grandparents); decision.push(parents);
  branch(decision, VAR_INORDER, VAL_MIN);

  outputs = {
    {"grandparents", dcp::out(grandparents)},
    {"parents", dcp::out(parents)},
    {"children", dcp::out(children)}
  };
}
