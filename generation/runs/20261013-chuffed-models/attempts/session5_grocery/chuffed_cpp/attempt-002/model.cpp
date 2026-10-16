// Grocery: item prices (in cents) whose sum and product (in dollars) both equal the total price.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int total_price = instance.at("total_price");  // in cents
  int num_items = instance.at("num_items");

  // The product is taken in dollars: prod(p_i / 100) = total_price / 100, so in cents
  // the product of the n prices is total_price * 100^(n-1). It must fit in a 32-bit int.
  long long target = total_price;
  for (int i = 1; i < num_items; ++i) target *= 100;
  if (target > 2000000000LL) throw std::runtime_error("product does not fit in 32 bits");

  // prices[i] is the price of item i in cents
  vec<IntVar*> prices;
  createVars(prices, num_items, 1, total_price, true);

  // adding the prices gives the total price
  int_linear(prices, IRT_EQ, total_price);

  // every price divides the product of all prices, hence the target (prunes the search)
  for (int v = 1; v <= total_price; ++v)
    if (target % v != 0)
      for (int i = 0; i < num_items; ++i) int_rel(prices[i], IRT_NE, v);

  // multiplying the prices (in dollars) gives the same total price; partial products
  // never exceed the full product because every price is at least 1 cent
  IntVar* running = prices[0];
  for (int i = 1; i < num_items; ++i) {
    IntVar* next = newIntVar(1, static_cast<int>(target));
    int_times(running, prices[i], next);
    running = next;
  }
  int_rel(running, IRT_EQ, static_cast<int>(target));

  branch(prices, VAR_INORDER, VAL_MIN);
  json out = json::array();
  for (int i = 0; i < num_items; ++i) out.push_back(dcp::out(prices[i]));
  outputs = {{"prices", out}};
}
