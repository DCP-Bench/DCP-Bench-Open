// Allergy puzzle: match four friends with a surname and an allergy each, from the clues.
// Friends are indexed Debra = 0, Janet = 1, Hugh = 2, Rick = 3 (the output order in the statement).
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  const int DEBRA = 0, JANET = 1, HUGH = 2, RICK = 3;

  // each surname and each allergy holds the index of the friend who has it
  IntVar* baxter = newIntVar(0, 3);
  IntVar* lemon = newIntVar(0, 3);
  IntVar* malone = newIntVar(0, 3);
  IntVar* fleet = newIntVar(0, 3);
  IntVar* eggs = newIntVar(0, 3);
  IntVar* mold = newIntVar(0, 3);
  IntVar* nuts = newIntVar(0, 3);
  IntVar* ragweed = newIntVar(0, 3);

  // every friend has exactly one surname
  vec<IntVar*> surnames;
  surnames.push(baxter);
  surnames.push(lemon);
  surnames.push(malone);
  surnames.push(fleet);
  all_different(surnames);

  // every friend has exactly one allergy
  vec<IntVar*> allergies;
  allergies.push(eggs);
  allergies.push(mold);
  allergies.push(nuts);
  allergies.push(ragweed);
  all_different(allergies);

  // Rick is not allergic to mold
  int_rel(mold, IRT_NE, RICK);

  // Baxter is allergic to eggs: the Baxter friend is the egg-allergic friend
  int_rel(baxter, IRT_EQ, eggs);

  // Hugh is neither surnamed Lemon nor Fleet
  int_rel(lemon, IRT_NE, HUGH);
  int_rel(fleet, IRT_NE, HUGH);

  // Debra is allergic to ragweed
  int_rel(ragweed, IRT_EQ, DEBRA);

  // Janet (who is not Lemon) is neither allergic to eggs nor to mold
  int_rel(lemon, IRT_NE, JANET);
  int_rel(eggs, IRT_NE, JANET);
  int_rel(mold, IRT_NE, JANET);

  vec<IntVar*> all;
  for (int i = 0; i < surnames.size(); ++i) all.push(surnames[i]);
  for (int i = 0; i < allergies.size(); ++i) all.push(allergies[i]);
  branch(all, VAR_INORDER, VAL_MIN);

  outputs = {{"baxter", dcp::out(baxter)}, {"eggs", dcp::out(eggs)},
             {"fleet", dcp::out(fleet)},   {"lemon", dcp::out(lemon)},
             {"malone", dcp::out(malone)}, {"mold", dcp::out(mold)},
             {"nuts", dcp::out(nuts)},     {"ragweed", dcp::out(ragweed)}};
}
