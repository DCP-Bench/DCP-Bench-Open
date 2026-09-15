#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Grocery: four prices in cents that both add up to the total and multiply to
// it, once the multiplication is rescaled from euros to cents.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int64_t total_price = instance.at("total_price").get<int64_t>();
  const int num_items = instance.at("num_items").get<int>();

  std::vector<IntVar> prices;
  for (int i = 0; i < num_items; ++i) {
    prices.push_back(model.NewIntVar(Domain(1, total_price)));
  }

  LinearExpr sum_prices;
  for (int i = 0; i < num_items; ++i) sum_prices += prices[i];
  model.AddEquality(sum_prices, total_price);

  // The product is taken in cents, so the euro-denominated total is scaled by
  // 100 once per extra factor.
  int64_t scaled_total = total_price;
  for (int i = 0; i < num_items - 1; ++i) scaled_total *= 100;

  // Chain the multiplication two factors at a time.  Every price is at least
  // one, so no partial product can exceed the final one; bounding them that
  // way keeps the intermediate domains small.
  IntVar running = prices[0];
  for (int i = 1; i < num_items; ++i) {
    IntVar next = model.NewIntVar(Domain(1, scaled_total));
    model.AddMultiplicationEquality(next, {running, prices[i]});
    running = next;
  }
  model.AddEquality(running, scaled_total);

  json out = json::array();
  for (const IntVar& p : prices) out.push_back(p.index());
  outputs = {{"prices", out}};
}
