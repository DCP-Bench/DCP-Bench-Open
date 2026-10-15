#include "dcp.h"
#include <algorithm>

// Revenue maximisation: flight legs have limited seats, and packages of
// itineraries are sold at a fixed price. Choose how many units of each package
// to sell, within its estimated demand and the seats left on every leg it uses,
// so that total revenue is maximised.
class RevenueMaximization : public dcp::Space {
 protected:
  IntVarArray packages_to_sell;  // units of each package to sell
  IntVar max_revenue;            // total revenue of the units sold

 public:
  explicit RevenueMaximization(const json& instance) {
    std::vector<int> demand = instance.at("demand").get<std::vector<int>>();
    std::vector<int> revenue = instance.at("revenue").get<std::vector<int>>();
    std::vector<int> seats = instance.at("available_seats").get<std::vector<int>>();
    const json& delta = instance.at("delta");   // delta[p][l] = 1 if package p uses leg l
    int np = static_cast<int>(demand.size());
    int nl = static_cast<int>(seats.size());

    // units of each package sold: at most the package's estimated demand
    int max_demand = *std::max_element(demand.begin(), demand.end());
    packages_to_sell = IntVarArray(*this, np, 0, max_demand);
    for (int p = 0; p < np; ++p)
      rel(*this, packages_to_sell[p] <= demand[p]);

    // the seats reserved on a leg are the units of every package using that leg,
    // and cannot exceed the leg's available seats
    for (int l = 0; l < nl; ++l) {
      IntVarArgs users;
      for (int p = 0; p < np; ++p)
        if (delta[p][l].get<int>() == 1) users << packages_to_sell[p];
      if (users.size() > 0)
        linear(*this, IntArgs::create(users.size(), 1, 0), users, IRT_LQ, seats[l]);
    }

    // total revenue: the price of each package times the units sold
    IntVarArgs sold;
    for (int p = 0; p < np; ++p) sold << packages_to_sell[p];
    max_revenue = expr(*this, sum(IntArgs(revenue), sold));

    // sell the units that decide the revenue first, trying the most units first
    branch(*this, packages_to_sell, INT_VAR_SIZE_MIN(), INT_VAL_MAX());
    maximize(max_revenue);
    output("packages_to_sell", packages_to_sell);
    output("max_revenue", max_revenue);
  }

  RevenueMaximization(RevenueMaximization& s) : dcp::Space(s) {
    packages_to_sell.update(*this, s.packages_to_sell);
    max_revenue.update(*this, s.max_revenue);
  }
  Gecode::Space* copy() override { return new RevenueMaximization(*this); }
};

DCP_MODEL(RevenueMaximization)
