// Abbot's puzzle: 100 bushels of corn are distributed among 100 people; find the number of men, women and children.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // the counts are at most 100 people (problem constant, stated in the description)
  IntVar* men = newIntVar(0, 100);
  IntVar* women = newIntVar(0, 100);
  IntVar* children = newIntVar(0, 100);

  // there are 100 people in total
  vec<IntVar*> people;
  people.push(men);
  people.push(women);
  people.push(children);
  int_linear(people, IRT_EQ, 100);

  // each man received three bushels, each woman two and each child half a bushel, 100 bushels in total
  // (doubled to stay in integers: 6*men + 4*women + children = 200)
  vec<int> twice_bushels;
  twice_bushels.push(6);
  twice_bushels.push(4);
  twice_bushels.push(1);
  int_linear(twice_bushels, people, IRT_EQ, 200);

  // there are five times as many women as men
  vec<int> ratio;
  ratio.push(1);
  ratio.push(-5);
  vec<IntVar*> men_women;
  men_women.push(women);
  men_women.push(men);
  int_linear(ratio, men_women, IRT_EQ, 0);

  branch(people, VAR_INORDER, VAL_MIN);

  outputs = {{"men", dcp::out(men)}, {"women", dcp::out(women)}, {"children", dcp::out(children)}};
}
