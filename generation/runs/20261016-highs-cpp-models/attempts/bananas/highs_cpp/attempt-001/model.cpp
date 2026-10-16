// Bananas puzzle: buy 100 fruits (bananas, oranges, mangoes, apples) for exactly
// 100 dollars. All four types must be bought, and bananas and apples should be
// of minimum quantity, so the objective minimises bananas + apples.
//
// Prices, in units of 1/315 dollar (315 = lcm of 5, 7, 9):
//   five bananas cost three dollars:  189 per banana
//   seven oranges cost five dollars:  225 per orange
//   nine mangoes cost seven dollars:  245 per mango
//   three apples cost nine dollars:   945 per apple
// 100 dollars is 31500 units.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const int fruits = 100;
  const double budget = 31500;

  dcp::Lin bananas = dcp::new_var(h, 1, fruits);
  dcp::Lin oranges = dcp::new_var(h, 1, fruits);
  dcp::Lin mangoes = dcp::new_var(h, 1, fruits);
  dcp::Lin apples = dcp::new_var(h, 1, fruits);

  // I need to purchase 100 fruits in 100 dollars.
  dcp::add_row(h, bananas + oranges + mangoes + apples, fruits, fruits);
  dcp::add_row(h, 189 * bananas + 225 * oranges + 245 * mangoes + 945 * apples, budget, budget);

  // all types of fruits need to be purchased, but I do not like banana and apple,
  // so these should be of minimum quantity.
  out.minimize(bananas + apples);

  out.add("apples", apples);
  out.add("bananas", bananas);
  out.add("mangoes", mangoes);
  out.add("oranges", oranges);
}
