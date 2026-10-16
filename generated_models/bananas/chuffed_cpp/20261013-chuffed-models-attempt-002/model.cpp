// Bananas: buy 100 fruits for exactly 100 dollars, at least one of each kind,
// with as few bananas and apples as possible.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // quantity bought of each fruit; at most 100 fruits are bought in total
  IntVar* bananas = newIntVar(1, 100);
  IntVar* oranges = newIntVar(1, 100);
  IntVar* mangoes = newIntVar(1, 100);
  IntVar* apples = newIntVar(1, 100);

  // I need to purchase 100 fruits
  vec<IntVar*> all;
  all.push(bananas); all.push(oranges); all.push(mangoes); all.push(apples);
  int_linear(all, IRT_EQ, 100);

  // in 100 dollars: banana 3/5, orange 5/7, mango 7/9, apple 9/3 dollars each.
  // Multiplying every price by 315 = 5*7*9 keeps the equation in integers:
  // 189*bananas + 225*oranges + 245*mangoes + 945*apples = 100 * 315
  vec<int> price;
  price.push(189); price.push(225); price.push(245); price.push(945);
  int_linear(price, all, IRT_EQ, 31500);

  // I do not like bananas and apples: minimize their quantity
  IntVar* disliked = newIntVar(2, 200);
  vec<IntVar*> two;
  two.push(bananas); two.push(apples);
  int_linear(two, IRT_EQ, disliked);

  branch(all, VAR_INORDER, VAL_MIN);
  optimize(disliked, OPT_MIN);

  outputs = {{"bananas", dcp::out(bananas)}, {"oranges", dcp::out(oranges)},
             {"mangoes", dcp::out(mangoes)}, {"apples", dcp::out(apples)}};
}
