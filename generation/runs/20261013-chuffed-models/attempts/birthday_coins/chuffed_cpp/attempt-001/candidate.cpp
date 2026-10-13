// Birthday coins: Tommy has 15 coins (half-crowns, shillings and sixpences) worth 1 pound 5s 6d.
// How many half-crowns?
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // coin values in pence (problem constants, from the old British currency):
  // half-crown = 2*12 + 6 = 30, shilling = 12, sixpence = 6
  const int kHalfCrown = 30, kShilling = 12, kSixpence = 6;
  // 15 coins; 1 pound 5s 6d = 240 + 5*12 + 6 = 306 pence
  const int kCoins = 15, kTotalPence = 240 + 5 * 12 + 6;

  // numbers of each kind of coin; he was given all three kinds, so at least one of each
  IntVar* half_crowns = newIntVar(1, kCoins);
  IntVar* shillings = newIntVar(1, kCoins);
  IntVar* sixpences = newIntVar(1, kCoins);
  vec<IntVar*> counts;
  counts.push(half_crowns);
  counts.push(shillings);
  counts.push(sixpences);

  // Tommy was given 15 coins
  int_linear(counts, IRT_EQ, kCoins);

  // the coins add up to 1 pound 5s 6d
  vec<int> value;
  value.push(kHalfCrown);
  value.push(kShilling);
  value.push(kSixpence);
  int_linear(value, counts, IRT_EQ, kTotalPence);

  branch(counts, VAR_INORDER, VAL_MIN);
  outputs = {{"half_crowns", dcp::out(half_crowns)}};
}
