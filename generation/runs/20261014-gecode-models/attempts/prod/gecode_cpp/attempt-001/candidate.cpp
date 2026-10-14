#include "dcp.h"

#include <algorithm>
#include <numeric>

// Production planning: choose how many units x[j] of each product j to make so
// that the total profit is as large as possible. Making one unit of product j
// takes 1/a[j] of the shared budget b, and x[j] never exceeds its capacity u[j].
class Prod : public dcp::Space {
 protected:
  IntVarArray x;   // x[j]: units of product j
  IntVar total;    // total profit

 public:
  explicit Prod(const json& instance) {
    std::vector<int> a = instance.at("a").get<std::vector<int>>();
    std::vector<int> c = instance.at("c").get<std::vector<int>>();
    std::vector<int> u = instance.at("u").get<std::vector<int>>();
    int b = instance.at("b").get<int>();
    int n = static_cast<int>(a.size());

    int max_u = *std::max_element(u.begin(), u.end());
    x = IntVarArray(*this, n, 0, max_u);

    // each X[j] is between 0 and its capacity u[j]
    for (int j = 0; j < n; ++j) rel(*this, x[j] <= u[j]);

    // the sum of X[j] / a[j] is at most b. Multiply by L, the lcm of the a[j],
    // so that every coefficient L / a[j] is an integer.
    long long L = 1;
    for (int j = 0; j < n; ++j) L = std::lcm(L, static_cast<long long>(a[j]));
    IntArgs time_coeff(n), profit_coeff(n);
    IntVarArgs xs;
    for (int j = 0; j < n; ++j) {
      time_coeff[j] = static_cast<int>(L / a[j]);
      profit_coeff[j] = c[j];
      xs << x[j];
    }
    linear(*this, time_coeff, xs, IRT_LQ, static_cast<int>(L * b));

    // total profit is the sum of c[j] * X[j]
    total = expr(*this, sum(profit_coeff, xs));

    // branch on products with the largest profit per unit of time first, and
    // try the largest number of units first
    std::vector<int> order(n);
    std::iota(order.begin(), order.end(), 0);
    std::stable_sort(order.begin(), order.end(), [&](int p, int q) {
      return static_cast<long long>(c[p]) * a[p] > static_cast<long long>(c[q]) * a[q];
    });
    IntVarArgs ordered;
    for (int j : order) ordered << x[j];
    branch(*this, ordered, INT_VAR_NONE(), INT_VAL_MAX());

    maximize(total);
    output("total_profit", total);
    output("x", x);
  }

  Prod(Prod& s) : dcp::Space(s) {
    x.update(*this, s.x);
    total.update(*this, s.total);
  }
  Gecode::Space* copy() override { return new Prod(*this); }
};

DCP_MODEL(Prod)
