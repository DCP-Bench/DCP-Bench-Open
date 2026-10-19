// Production problem (prod): choose integer production quantities X[j] for each product j
// with 0 <= X[j] <= u[j], so that the sum of X[j] / a[j] (time used per unit) is at most b,
// and maximise the total profit, the sum of c[j] * X[j].
#include "dcp.h"

#include <numeric>

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const auto& a = instance.at("a");
  const auto& c = instance.at("c");
  const auto& u = instance.at("u");
  const long long b = instance.at("b").get<long long>();
  const int n = static_cast<int>(a.size());

  // The time constraint has fractional coefficients 1/a[j]. Multiply it by L = lcm(a[j])
  // so every coefficient is the integer L / a[j] and the right-hand side is L * b.
  long long L = 1;
  for (int j = 0; j < n; ++j) {
    long long aj = a[j].get<long long>();
    L = L / std::gcd(L, aj) * aj;
  }

  // production quantity of each product, integer between 0 and its upper bound
  std::vector<dcp::Lin> X;
  for (int j = 0; j < n; ++j) X.push_back(dcp::new_var(h, 0, u[j].get<double>()));

  // the time used by all products is at most the time available
  dcp::Lin time;
  for (int j = 0; j < n; ++j) time = time + (static_cast<double>(L / a[j].get<long long>())) * X[j];
  dcp::add_row(h, time, -kHighsInf, static_cast<double>(L * b));

  // total profit is the sum of the unit profit times the production quantity
  dcp::Lin profit;
  for (int j = 0; j < n; ++j) profit = profit + c[j].get<double>() * X[j];
  out.maximize(profit);

  out.add("total_profit", profit);
  out.add("x", X);
}
