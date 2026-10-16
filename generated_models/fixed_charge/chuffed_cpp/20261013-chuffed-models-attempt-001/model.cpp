// Fixed charge production: choose how much of each product (shirts, shorts, pants) to make and which machines to rent, to maximize profit minus the machine rental costs.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int np = instance.at("num_products");
  int nm = instance.at("num_machines");
  std::vector<int> capacity = instance.at("capacity").get<std::vector<int>>();     // capacity of each resource (labor, cloth)
  std::vector<int> renting = instance.at("renting_cost").get<std::vector<int>>();  // rent of each machine
  int max_prod = instance.at("max_production");                                     // upper bound on the output of each product
  const json& product = instance.at("product");  // product[p] = [profit per unit, machine that makes p]
  const json& use = instance.at("use");          // use[p][r] = amount of resource r needed per unit of product p
  int nr = static_cast<int>(capacity.size());

  // x[p] = number of units of product p produced
  vec<IntVar*> x;
  createVars(x, np, 0, max_prod);

  // made[p] = 1 if product p is produced at all
  vec<BoolView> made;
  createVars(made, np);
  for (int p = 0; p < np; ++p) int_rel_reif(x[p], IRT_GT, 0, made[p]);

  // rented[m] = 1 if machine m is rented
  vec<BoolView> rented;
  createVars(rented, nm);
  for (int m = 0; m < nm; ++m) {
    // a product made on machine m requires machine m to be rented
    vec<BoolView> users;
    for (int p = 0; p < np; ++p) {
      if (product[p][1].get<int>() != m) continue;
      vec<BoolView> need, none;
      need.push(rented[m]);
      none.push(made[p]);
      bool_clause(need, none);
      users.push(made[p]);
    }
    // machine m is rented only if some product is made on it
    vec<BoolView> only_if, not_rented;
    for (int k = 0; k < users.size(); ++k) only_if.push(users[k]);
    not_rented.push(rented[m]);
    bool_clause(only_if, not_rented);
  }

  // rented machines and produced units must fit into the resource capacities
  for (int r = 0; r < nr; ++r) {
    // the resource r used by all products
    vec<int> coef;
    vec<IntVar*> vars;
    for (int p = 0; p < np; ++p) {
      coef.push(use[p][r].get<int>());
      vars.push(x[p]);
    }
    int_linear(coef, vars, IRT_LE, capacity[r]);
  }

  // rented machines as 0..1 integers, for the objective
  vec<IntVar*> rent_int;
  for (int m = 0; m < nm; ++m) {
    IntVar* v = newIntVar(0, 1);
    bool2int(rented[m], v);
    rent_int.push(v);
  }

  // z is the profit of the production minus the rent of the machines
  int lo = 0, hi = 0;
  for (int m = 0; m < nm; ++m) lo -= renting[m];
  for (int p = 0; p < np; ++p) hi += product[p][0].get<int>() * max_prod;
  IntVar* z = newIntVar(lo, hi);
  vec<IntVar*> terms;
  vec<int> weights;
  for (int p = 0; p < np; ++p) {
    terms.push(x[p]);
    weights.push(product[p][0].get<int>());
  }
  for (int m = 0; m < nm; ++m) {
    terms.push(rent_int[m]);
    weights.push(-renting[m]);
  }
  int_linear(weights, terms, IRT_EQ, z);

  // produce as much as the resources allow, and maximize the profit
  branch(x, VAR_INORDER, VAL_MAX);
  optimize(z, OPT_MAX);

  outputs = {{"z", dcp::out(z)}};
}
