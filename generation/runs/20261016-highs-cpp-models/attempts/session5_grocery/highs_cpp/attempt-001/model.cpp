// Session 5 grocery: a kid buys num_items items. The cashier charges total_price when adding
// the item prices, and the same total comes out when the prices are multiplied (in cents:
// the product of the prices in dollars, times 100). Find the prices of the items, in cents.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("num_items").get<int>();
  long long total = instance.at("total_price").get<long long>();

  // The product is taken in dollars and reported in cents: prod(prices) / 100^(n-1) = total,
  // so prod(prices) = total * 100^(n-1).
  double product = static_cast<double>(total);
  for (int i = 1; i < n; i++) product *= 100.0;

  // Bits needed for a price up to total.
  int bits = 0;
  while ((1LL << bits) - 1 < total) bits++;

  // Each item has a price in whole cents, at least 1 because the product is positive,
  // and at most total because the prices add up to total.
  std::vector<dcp::Lin> price;
  for (int i = 0; i < n; i++) price.push_back(dcp::new_var(h, 1, static_cast<double>(total)));

  // the prices of the items added together give the total price
  dcp::Lin sum;
  for (const auto& p : price) sum = sum + p;
  dcp::add_row(h, sum, static_cast<double>(total), static_cast<double>(total));

  // each price is written in binary digits: price = sum of 2^k times digit k
  std::vector<std::vector<dcp::Lin>> digit(n);
  for (int i = 0; i < n; i++) {
    dcp::Lin value;
    for (int k = 0; k < bits; k++) {
      digit[i].push_back(dcp::new_var(h, 0, 1));
      value = value + static_cast<double>(1LL << k) * digit[i][k];
    }
    dcp::add_row(h, price[i] - value, 0, 0);
  }

  // the running product of the prices so far: partial[0] is the first price, and
  // partial[i] = partial[i-1] * price[i], built with one product term per binary digit of price[i]
  dcp::Lin partial = price[0];
  for (int i = 1; i < n; i++) {
    // each digit term w_k equals the running product when digit k is 1, and 0 when it is 0
    // (the running product never exceeds the final product, which bounds the big-M)
    dcp::Lin next_sum;
    for (int k = 0; k < bits; k++) {
      dcp::Lin w = dcp::new_var(h, 0, product);
      dcp::Lin b = digit[i][k];
      dcp::add_row(h, w - b * product, -kHighsInf, 0);            // w <= product * digit
      dcp::add_row(h, w - partial, -kHighsInf, 0);                // w <= running product
      dcp::add_row(h, w - partial - product * b, -product, kHighsInf);  // w >= running product when digit is 1
      next_sum = next_sum + static_cast<double>(1LL << k) * w;
    }
    // the running product after item i is the sum of the digit terms
    dcp::Lin next = dcp::new_var(h, 0, product);
    dcp::add_row(h, next - next_sum, 0, 0);
    partial = next;
  }

  // the product of all the prices, in cents, equals the total
  dcp::add_row(h, partial, product, product);

  out.add("prices", price);
}
