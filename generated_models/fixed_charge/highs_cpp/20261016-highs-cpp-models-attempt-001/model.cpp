// Fixed-charge production planning: a company makes shirts, shorts and pants from
// labor and cloth. Each product can be made only on a machine that must be rented.
// Maximise the profit on the products minus the rent of the machines used.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int num_products = instance.at("num_products").get<int>();
  int num_machines = instance.at("num_machines").get<int>();
  int max_production = instance.at("max_production").get<int>();
  const json& product = instance.at("product");      // product[p][0] is the profit per unit of p
  const json& use = instance.at("use");              // use[p][r] is the amount of resource r per unit of p
  const json& capacity = instance.at("capacity");    // capacity[r] is the available amount of resource r
  const json& renting_cost = instance.at("renting_cost");
  std::vector<int> machine_of = {instance.at("shirtM").get<int>(),
                                 instance.at("shortM").get<int>(),
                                 instance.at("pantM").get<int>()};

  // the number of units made of each product, from 0 up to the largest production
  std::vector<dcp::Lin> made(num_products);
  for (int p = 0; p < num_products; ++p) made[p] = dcp::new_var(h, 0, max_production);

  // whether each machine is rented (1) or not (0)
  std::vector<dcp::Lin> rented(num_machines);
  for (int m = 0; m < num_machines; ++m) rented[m] = dcp::new_var(h, 0, 1);

  // the labor hours and the cloth used by all products stay within the capacity of each resource
  for (size_t r = 0; r < capacity.size(); ++r) {
    dcp::Lin used;
    for (int p = 0; p < num_products; ++p) {
      double amount = use.at(p).at(r).get<double>();
      used = used + amount * made[p];
    }
    dcp::add_row(h, used, -kHighsInf, capacity.at(r).get<double>());
  }

  // a product can be made only when its machine is rented: its production is at most
  // max_production (the largest production, from the data) times the rent indicator, so zero otherwise
  for (int p = 0; p < num_products; ++p) {
    int m = machine_of.at(p);
    dcp::add_row(h, made[p] - static_cast<double>(max_production) * rented[m], -kHighsInf, 0);
  }

  // the profit from the products minus the rent of the machines
  dcp::Lin profit;
  for (int p = 0; p < num_products; ++p) {
    double unit_profit = product.at(p).at(0).get<double>();
    profit = profit + unit_profit * made[p];
  }
  dcp::Lin rent;
  for (int m = 0; m < num_machines; ++m) {
    double cost = renting_cost.at(m).get<double>();
    rent = rent + cost * rented[m];
  }
  dcp::Lin net = profit - rent;

  out.add("z", net);
  out.maximize(net);
}
