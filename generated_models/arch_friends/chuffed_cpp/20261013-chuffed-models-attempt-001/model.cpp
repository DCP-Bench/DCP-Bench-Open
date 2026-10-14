// Arch friends: Harriet bought four pairs of shoes at four stores; find the order of the purchases (1 to 4) and the store of each.
// The same value denotes the same shoe or store, so each category is a permutation of 1 to 4.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // the problem has no instance data; positions of purchases run from 1 to 4

  // the position in Harriet's sequence of each shoe
  IntVar* ecru = newIntVar(1, 4);
  IntVar* fuchsia = newIntVar(1, 4);
  IntVar* purple = newIntVar(1, 4);
  IntVar* suede = newIntVar(1, 4);

  // the position of each store in Harriet's sequence
  IntVar* foot = newIntVar(1, 4);
  IntVar* heels = newIntVar(1, 4);
  IntVar* palace = newIntVar(1, 4);
  IntVar* tootsies = newIntVar(1, 4);

  // each shoe is bought at a different stop
  vec<IntVar*> shoes;
  shoes.push(ecru); shoes.push(fuchsia); shoes.push(purple); shoes.push(suede);
  all_different(shoes);

  // each store is a different stop
  vec<IntVar*> stores;
  stores.push(foot); stores.push(heels); stores.push(palace); stores.push(tootsies);
  all_different(stores);

  // clue 1: Harriet bought fuchsia flats at Heels in a Handcart, so the two positions are equal
  int_rel(fuchsia, IRT_EQ, heels);

  // clue 3: the Foot Farm was Harriet's second stop
  int_rel(foot, IRT_EQ, 2);

  // clue 4: two stops after leaving The Shoe Palace she bought the suede sandals
  vec<IntVar*> pair_s;
  pair_s.push(suede); pair_s.push(palace);
  vec<int> pair_c;
  pair_c.push(1); pair_c.push(-1);
  int_linear(pair_c, pair_s, IRT_EQ, 2);

  // clue 2: the store just after the purple pumps was not Tootsies (if the purple pumps were the last stop there is no such store)
  // last_stop is true when the purple pumps are the fourth stop
  BoolView last_stop = newBoolVar();
  int_rel_reif(purple, IRT_EQ, 4, last_stop);
  // next_is_tootsies is true when Tootsies is exactly one stop after the purple pumps
  BoolView next_is_tootsies = newBoolVar();
  vec<IntVar*> pair_t;
  pair_t.push(tootsies); pair_t.push(purple);
  int_linear(pair_c, pair_t, IRT_EQ, 1, next_is_tootsies);
  // last_stop or not next_is_tootsies
  vec<BoolView> pos, neg;
  pos.push(last_stop);
  neg.push(next_is_tootsies);
  bool_clause(pos, neg);

  // the shoe positions drive the rest of the puzzle, so branch on them
  vec<IntVar*> decisions;
  decisions.push(purple); decisions.push(ecru); decisions.push(fuchsia); decisions.push(suede);
  branch(decisions, VAR_INORDER, VAL_MIN);

  outputs = {
    {"ecruespadrilles", dcp::out(ecru)},
    {"fuchsiaflats", dcp::out(fuchsia)},
    {"purplepumps", dcp::out(purple)},
    {"suedesandals", dcp::out(suede)},
    {"footfarm", dcp::out(foot)},
    {"heelsinahandcart", dcp::out(heels)},
    {"theshoepalace", dcp::out(palace)},
    {"tootsies", dcp::out(tootsies)}
  };
}
