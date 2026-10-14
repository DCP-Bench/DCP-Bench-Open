// Five people (Baker, Cooper, Fletcher, Miller, Smith) live on the five floors of an apartment house;
// each variable is the floor (1..5) a person lives on.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // B, C, F, M, S are the floors of Baker, Cooper, Fletcher, Miller and Smith
  IntVar* B = newIntVar(1, 5);
  IntVar* C = newIntVar(1, 5);
  IntVar* F = newIntVar(1, 5);
  IntVar* M = newIntVar(1, 5);
  IntVar* S = newIntVar(1, 5);

  // They all live on different floors
  vec<IntVar*> floors;
  floors.push(B); floors.push(C); floors.push(F); floors.push(M); floors.push(S);
  all_different(floors);

  // Baker does not live on the fifth floor
  int_rel(B, IRT_NE, 5);

  // Cooper does not live on the first floor
  int_rel(C, IRT_NE, 1);

  // Fletcher does not live on either the fifth or the first floor
  int_rel(F, IRT_NE, 5);
  int_rel(F, IRT_NE, 1);

  // Miller lives on a higher floor than does Cooper
  int_rel(C, IRT_LT, M);

  // Smith does not live on a floor adjacent to Fletcher's: S - F is not -1 or 1
  IntVar* sf = newIntVar(-4, 4);
  int_minus(S, F, sf);
  int_rel(sf, IRT_NE, 1);
  int_rel(sf, IRT_NE, -1);

  // Fletcher does not live on a floor adjacent to Cooper's: F - C is not -1 or 1
  IntVar* fc = newIntVar(-4, 4);
  int_minus(F, C, fc);
  int_rel(fc, IRT_NE, 1);
  int_rel(fc, IRT_NE, -1);

  // the floors are the decision variables
  branch(floors, VAR_INORDER, VAL_MIN);

  outputs = {{"B", dcp::out(B)}, {"C", dcp::out(C)}, {"F", dcp::out(F)},
             {"M", dcp::out(M)}, {"S", dcp::out(S)}};
}
