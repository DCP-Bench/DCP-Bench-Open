// Session 5 grocery: a kid buys num_items items. The cashier charges total_price when adding
// the item prices, and the same total comes out when the prices are multiplied (in cents:
// the product of the prices in dollars, times 100). Find the prices of the items, in cents.
#include <map>

#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("num_items").get<int>();
  long long total = instance.at("total_price").get<long long>();

  // The product is taken in dollars and reported in cents: prod(prices) / 100^(n-1) = total,
  // so prod(prices) = total * 100^(n-1).
  long long product = total;
  for (int i = 1; i < n; i++) product *= 100;

  // Each price is a whole number of cents, at most total, and it divides the product
  // (the product is the multiplication of all the prices).
  std::vector<long long> values;
  for (long long d = 1; d <= total; d++)
    if (product % d == 0) values.push_back(d);

  // pick[i][j] = 1 means item i costs values[j] cents
  std::vector<std::vector<dcp::Lin>> pick(n, std::vector<dcp::Lin>(values.size()));
  std::vector<dcp::Lin> price(n);
  for (int i = 0; i < n; i++) {
    // each item has exactly one price
    dcp::Lin one;
    for (size_t j = 0; j < values.size(); j++) {
      pick[i][j] = dcp::new_var(h, 0, 1);
      one = one + pick[i][j];
      price[i] = price[i] + static_cast<double>(values[j]) * pick[i][j];
    }
    dcp::add_row(h, one, 1, 1);
  }

  // the prices of the items, added together, give the total price
  dcp::Lin sum;
  for (const auto& p : price) sum = sum + p;
  dcp::add_row(h, sum, static_cast<double>(total), static_cast<double>(total));

  // the running product of the prices so far: each state is a value of the product so far,
  // and each arc picks the price of the next item, so the product runs through the states
  // until it reaches the required product
  std::map<long long, dcp::Lin> state;  // running product -> flow that arrives at it
  for (size_t j = 0; j < values.size(); j++) state[values[j]] = pick[0][j];

  for (int i = 1; i < n; i++) {
    std::map<long long, dcp::Lin> next;  // flow that leaves each new running product
    std::vector<dcp::Lin> used(values.size());
    for (const auto& [q, arriving] : state) {
      // the running product q is multiplied by one price of item i
      dcp::Lin leaving;
      for (size_t j = 0; j < values.size(); j++) {
        long long r = q * values[j];
        if (product % r != 0) continue;
        if (i == n - 1 && r != product) continue;  // the last item must reach the product
        dcp::Lin arc = dcp::new_var(h, 0, 1);
        leaving = leaving + arc;
        next[r] = next[r] + arc;
        used[j] = used[j] + arc;
      }
      // the flow that arrives at the running product q leaves it
      dcp::add_row(h, leaving - arriving, 0, 0);
    }
    // the arc taken for item i is the price chosen for item i
    for (size_t j = 0; j < values.size(); j++) dcp::add_row(h, used[j] - pick[i][j], 0, 0);
    state = next;
  }

  out.add("prices", price);
}
