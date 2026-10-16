#include "dcp.h"

// Fixed charge problem: a company manufactures shirts, shorts and pants. Each
// product is made on its own machine, which must be rented at a fixed cost.
// Each product earns a profit per unit and uses labour and cloth per unit, and
// both resources have a limited capacity. Maximise profit minus rental cost.
//
// Instance layout: product[p] = [profit per unit, machine of p];
// use[p][r] = amount of resource r per unit of p; capacity[r] = limit of r.
class FixedCharge : public dcp::Space {
 protected:
  IntVarArray make;  // make[p]: units of product p
  IntVarArray rent;  // rent[m]: 1 if machine m is rented, 0 otherwise
  IntVar z;          // profit minus rental cost

 public:
  explicit FixedCharge(const json& instance) {
    int P = instance.at("num_products").get<int>();
    int M = instance.at("num_machines").get<int>();
    int max_production = instance.at("max_production").get<int>();
    const json& product = instance.at("product");
    const json& use = instance.at("use");
    const json& capacity = instance.at("capacity");
    const json& renting_cost = instance.at("renting_cost");
    std::vector<int> resources = instance.at("resources").get<std::vector<int>>();

    make = IntVarArray(*this, P, 0, max_production);
    rent = IntVarArray(*this, M, 0, 1);

    // a product can only be made on a rented machine:
    // make[p] <= max_production * rent[machine of p]
    for (int p = 0; p < P; ++p) {
      int m = product[p][1].get<int>();
      IntVarArgs x;
      x << make[p] << rent[m];
      linear(*this, IntArgs({1, -max_production}), x, IRT_LQ, 0, IPL_BND);
    }

    // each resource (labour, cloth) has a limited capacity:
    // sum over products of use[p][r] * make[p] <= capacity[r]
    for (int r : resources) {
      IntArgs consumption(P);
      for (int p = 0; p < P; ++p) consumption[p] = use[p][r].get<int>();
      linear(*this, consumption, make, IRT_LQ, capacity[r].get<int>());
    }

    // profit on the products minus the renting cost of the machines equals z
    IntVarArgs terms;
    IntArgs weights(P + M + 1);
    int k = 0;
    for (int p = 0; p < P; ++p, ++k) {
      terms << make[p];
      weights[k] = product[p][0].get<int>();
    }
    for (int m = 0; m < M; ++m, ++k) {
      terms << rent[m];
      weights[k] = -renting_cost[m].get<int>();
    }
    int profit_ub = 0;
    int rent_lb = 0;
    for (int p = 0; p < P; ++p) profit_ub += product[p][0].get<int>() * max_production;
    for (int m = 0; m < M; ++m) rent_lb -= renting_cost[m].get<int>();
    z = IntVar(*this, rent_lb, profit_ub);
    terms << z;
    weights[k] = -1;
    linear(*this, weights, terms, IRT_EQ, 0);

    branch(*this, rent, INT_VAR_NONE(), INT_VAL_MAX());
    branch(*this, make, INT_VAR_SIZE_MIN(), INT_VAL_SPLIT_MIN());
    maximize(z);
    output("z", z);
  }

  FixedCharge(FixedCharge& s) : dcp::Space(s) {
    make.update(*this, s.make);
    rent.update(*this, s.rent);
    z.update(*this, s.z);
  }
  Gecode::Space* copy() override { return new FixedCharge(*this); }
};

DCP_MODEL(FixedCharge)
