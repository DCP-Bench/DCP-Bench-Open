#include "dcp.h"

// Grocery prices: a kid buys n items. The cashier's total is the sum of the item
// prices, and it is also the product of the item prices (the cashier multiplied by
// mistake, yet the total agrees). Find the item prices in cents.
class Grocery : public dcp::Space {
 protected:
  IntVarArray price;  // price[i]: price of item i in cents

 public:
  explicit Grocery(const json& instance) {
    int n = instance.at("num_items").get<int>();
    int total = instance.at("total_price").get<int>();

    // every item costs at least 1 cent, so each price is at most total - (n - 1)
    price = IntVarArray(*this, n, 1, total - (n - 1));

    // the cashier's total is the sum of the item prices
    linear(*this, price, IRT_EQ, total);

    // the cashier's total is also the product of the item prices, taken in dollars.
    // The prices are in cents, so the product of the cent prices is total * 100^(n-1):
    // [200, 200] gives 2.00 * 2.00 = 4.00 dollars = 400 cents.
    // Chain the products: prod is the product of the first k prices. Every price is at
    // least 1, so each partial product is at most the full product, which bounds the
    // domains. The chain avoids an overflowing n-fold product expression.
    long long full = total;
    for (int i = 1; i < n; ++i) full *= 100;
    IntVar prod = price[0];
    for (int i = 1; i < n; ++i) {
      IntVar next(*this, 1, static_cast<int>(full));
      mult(*this, prod, price[i], next);
      prod = next;
    }
    rel(*this, prod == static_cast<int>(full));

    // the items are interchangeable and the answer lists prices with no order, so
    // the prices are given in non-decreasing order
    for (int i = 0; i + 1 < n; ++i)
      rel(*this, price[i], IRT_LQ, price[i + 1]);

    branch(*this, price, INT_VAR_NONE(), INT_VAL_MIN());
    output("prices", price);
  }

  Grocery(Grocery& s) : dcp::Space(s) {
    price.update(*this, s.price);
  }
  Gecode::Space* copy() override { return new Grocery(*this); }
};

DCP_MODEL(Grocery)
