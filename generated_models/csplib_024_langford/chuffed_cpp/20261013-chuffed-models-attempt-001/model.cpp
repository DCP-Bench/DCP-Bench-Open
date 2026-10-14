// Langford pairing: place two copies of each number 1 to k in a sequence of 2k so that the two copies of i have i numbers between them.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int k = instance.at("k");
  int slots = 2 * k;

  // occurrence[j] is the position of occurrence j of the numbers: j < k is the first copy of number j+1, j >= k is the second copy of number j-k+1
  vec<IntVar*> occurrence;
  createVars(occurrence, slots, 0, slots - 1);
  // inverse of occurrence: number_at[p] is the occurrence index placed at position p
  vec<IntVar*> number_at;
  createVars(number_at, slots, 0, slots - 1);
  inverse(occurrence, number_at);

  // every position holds exactly one copy: the inverse link above makes the placement a permutation of the positions
  // the copies of number i are i+1 positions apart, so there are i numbers between them
  vec<int> gap;
  gap.push(1); gap.push(-1);
  for (int i = 1; i <= k; ++i) {
    vec<IntVar*> pair;
    pair.push(occurrence[k + i - 1]); pair.push(occurrence[i - 1]);
    int_linear(gap, pair, IRT_EQ, i + 1);
  }

  // value_of_occurrence[j] is the number carried by occurrence j
  vec<int> value_of_occurrence;
  for (int j = 0; j < slots; ++j) value_of_occurrence.push((j % k) + 1);

  // sol[p] is the number at position p, read through the placement
  vec<IntVar*> sol;
  for (int p = 0; p < slots; ++p) {
    IntVar* v = newIntVar(1, k);
    array_int_element(number_at[p], value_of_occurrence, v);
    sol.push(v);
  }

  // branch on the first copies of the numbers, in order of their values
  vec<IntVar*> firsts;
  for (int i = 0; i < k; ++i) firsts.push(occurrence[i]);
  branch(firsts, VAR_INORDER, VAL_MIN);

  json seq = json::array();
  for (int p = 0; p < slots; ++p) seq.push_back(dcp::out(sol[p]));
  outputs = {{"sol", seq}};
}
