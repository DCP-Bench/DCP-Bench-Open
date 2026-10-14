// Huey, Dewey and Louie cannot lie: find who is guilty so that all three statements are true.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // huey, dewey, louie = 1 if that nephew is guilty
  vec<IntVar*> g;
  createVars(g, 3, 0, 1, true);
  IntVar* huey = g[0];
  IntVar* dewey = g[1];
  IntVar* louie = g[2];

  // Huey: Dewey and Louie have an equal share in it; if one is guilty, so is the other
  int_rel(dewey, IRT_EQ, louie);

  // Dewey: if Huey is guilty, then so am I
  int_rel(huey, IRT_LE, dewey);

  // Louie: Dewey and I are not both guilty
  bin_linear(dewey, louie, IRT_LE, 1);

  branch(g, VAR_INORDER, VAL_MIN);
  outputs = {{"huey", dcp::out(huey)}, {"dewey", dcp::out(dewey)}, {"louie", dcp::out(louie)}};
}
