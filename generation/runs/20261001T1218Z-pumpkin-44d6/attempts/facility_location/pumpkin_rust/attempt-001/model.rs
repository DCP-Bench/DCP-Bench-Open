// Facility location: decide which warehouses to open and how many units each
// open warehouse ships to each region, meeting every region's demand at the
// least total cost (fixed cost of the open warehouses plus shipping cost),
// subject to the company's three rules about which warehouses may be open.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let fixed_costs = inst.ints("fixed_costs"); // weekly fixed cost of each warehouse
    let max_shipping = inst.int("max_shipping"); // most units one warehouse ships per week
    let demands = inst.ints("demands"); // weekly demand of each region
    let shipping_costs = inst.matrix("shipping_costs"); // shipping_costs[i][j]: unit cost from warehouse i to region j
    let num_companies = fixed_costs.len();
    let num_regions = demands.len();

    // The rules below name the cities of the problem statement. The instance
    // lists them in this order (New York, Los Angeles, Chicago, Atlanta), as
    // the reference assumes.
    let new_york = 0;
    let los_angeles = 1;
    let atlanta = 3;

    // open_warehouse[i] is true when warehouse i is open.
    let open_warehouse: Vec<Lit> = (0..num_companies).map(|_| solver.new_literal()).collect();
    // ships[i][j] is the number of units warehouse i ships to region j, from 0 to max_shipping.
    let ships: Vec<Vec<Var>> = (0..num_companies)
        .map(|_| (0..num_regions).map(|_| solver.new_bounded_integer(0, max_shipping)).collect())
        .collect();
    // total_cost is the cost of the whole plan; the reference bounds it by 0 and 10000.
    let total_cost = solver.new_bounded_integer(0, 10000);

    // Each warehouse ships at most max_shipping units in total, and nothing at
    // all when it is closed: sum(ships[i]) <= max_shipping * open_warehouse[i].
    let capacity = solver.new_constraint_tag();
    for i in 0..num_companies {
        let mut terms: Vec<Term> = ships[i].iter().map(|v| v.scaled(1)).collect();
        if max_shipping != 0 {
            terms.push(open_warehouse[i].get_integer_variable().scaled(-max_shipping));
        }
        solver
            .add_constraint(pumpkin_solver::less_than_or_equals(terms, 0, capacity))
            .post();
    }

    // Each region receives at least its demand: sum over warehouses of
    // ships[i][j] >= demands[j], posted as the negated sum <= -demand.
    let demand = solver.new_constraint_tag();
    for j in 0..num_regions {
        let terms: Vec<Term> = (0..num_companies).map(|i| ships[i][j].scaled(-1)).collect();
        solver
            .add_constraint(pumpkin_solver::less_than_or_equals(terms, -demands[j], demand))
            .post();
    }

    // The total cost is the fixed costs of the open warehouses plus the units
    // shipped times their unit shipping cost. Zero coefficients are left out
    // because Pumpkin cannot take them.
    let mut terms: Vec<Term> = vec![total_cost.scaled(-1)];
    for i in 0..num_companies {
        if fixed_costs[i] != 0 {
            terms.push(open_warehouse[i].get_integer_variable().scaled(fixed_costs[i]));
        }
        for j in 0..num_regions {
            if shipping_costs[i][j] != 0 {
                terms.push(ships[i][j].scaled(shipping_costs[i][j]));
            }
        }
    }
    let cost = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(terms, 0, cost))
        .post();

    // Rule 1: if the New York warehouse is open, the Los Angeles one is too.
    let rule_1 = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::clause(
            vec![!open_warehouse[new_york], open_warehouse[los_angeles]], rule_1))
        .post();

    // Rule 2: at most three warehouses are open.
    let rule_2 = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::boolean_less_than_or_equals(
            vec![1; num_companies], open_warehouse.clone(), 3, rule_2))
        .post();

    // Rule 3: the Atlanta or the Los Angeles warehouse is open.
    let rule_3 = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::clause(
            vec![open_warehouse[atlanta], open_warehouse[los_angeles]], rule_3))
        .post();

    let mut m = Model::new();
    m.put("total_cost", total_cost);
    m.put("open_warehouse", open_warehouse);
    m.put("ships", ships);
    m.minimise(total_cost);
    m
}
