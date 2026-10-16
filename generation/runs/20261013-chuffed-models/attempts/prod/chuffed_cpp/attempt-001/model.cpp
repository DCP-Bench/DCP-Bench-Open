// Production planning: choose an integer production quantity x[j] for each product j, from 0 to u[j],
// so that the time used, the sum of x[j] / a[j], does not exceed b. Maximise the profit, the sum of c[j] * x[j].
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<int> a = instance.at("a").get<std::vector<int>>();
  std::vector<int> c = instance.at("c").get<std::vector<int>>();
  std::vector<int> u = instance.at("u").get<std::vector<int>>();
  int b = instance.at("b");
  int n = static_cast<int>(a.size());

  // x[j] is the quantity of product j, from 0 to u[j]
  vec<IntVar*> x;
  for (int j = 0; j < n; ++j) x.push(newIntVar(0, u[j]));

  // the time constraint sum x[j] / a[j] <= b has fractional coefficients, so it is multiplied
  // by L, the least common multiple of the a[j]: sum (L / a[j]) * x[j] <= L * b
  int L = 1;
  for (int j = 0; j < n; ++j) {
    int p = L, q = a[j];
    while (q != 0) {
      int r = p % q;
      p = q;
      q = r;
    }
    L = L / p * a[j];
  }
  vec<int> time_coef;
  for (int j = 0; j < n; ++j) time_coef.push(L / a[j]);

  // the production must fit in the available time b
  int_linear(time_coef, x, IRT_LE, L * b);

  // profit is the sum of c[j] * x[j]
  int max_profit = 0;
  for (int j = 0; j < n; ++j) max_profit += c[j] * u[j];
  vec<int> profit_coef;
  for (int j = 0; j < n; ++j) profit_coef.push(c[j]);
  IntVar* profit = newIntVar(0, max_profit);
  int_linear(profit_coef, x, IRT_EQ, profit);

  // try larger quantities first
  branch(x, VAR_INORDER, VAL_MAX);

  // maximise the profit
  optimize(profit, OPT_MAX);

  json quantities = json::array();
  for (int j = 0; j < n; ++j) quantities.push_back(dcp::out(x[j]));
  outputs = {{"x", quantities}, {"total_profit", dcp::out(profit)}};
}
