// Aircraft assignment: decide how many aircraft of each type fly each route so
// that every route's passenger demand is met, no type exceeds the aircraft it has,
// and the total operating cost is as small as possible.

// `sign * sum(coeffs[k] * vars[k])` as terms for a linear constraint. A zero
// coefficient would break Pumpkin, so those entries are dropped; if nothing is
// left the sum is the constant 0, written over a variable fixed at 0 because
// Pumpkin cannot post an empty linear constraint.
fn weighted(solver: &mut Solver, coeffs: &[i32], vars: &[Var], sign: i32) -> Vec<Term> {
    let mut terms: Vec<Term> = coeffs
        .iter()
        .zip(vars)
        .filter(|(&c, _)| c != 0)
        .map(|(&c, &v)| v.scaled(sign * c))
        .collect();
    if terms.is_empty() {
        terms.push(solver.new_bounded_integer(0, 0).scaled(1));
    }
    terms
}

fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let availability = inst.ints("availability"); // aircraft of each type that exist
    let demand = inst.ints("demand"); // passengers to carry on each route
    let capabilities = inst.matrix("capabilities"); // passengers one aircraft of type i carries on route j
    let costs = inst.matrix("costs"); // cost of flying one aircraft of type i on route j
    let num_aircraft = availability.len();
    let num_routes = demand.len();

    // allocation[i][j] is the number of aircraft of type i flying route j. As in
    // the reference, each entry ranges from 0 to the largest availability.
    let most = *availability.iter().max().unwrap();
    let allocation: Vec<Vec<Var>> = (0..num_aircraft)
        .map(|_| (0..num_routes).map(|_| solver.new_bounded_integer(0, most)).collect())
        .collect();

    // The aircraft of a type assigned over all routes do not exceed its availability.
    let fleet = solver.new_constraint_tag();
    for a in 0..num_aircraft {
        solver
            .add_constraint(pumpkin_solver::less_than_or_equals(
                allocation[a].clone(), availability[a], fleet))
            .post();
    }

    // The capacity assigned to each route meets its demand. Pumpkin only has
    // "<=", so sum(allocation * capacity) >= demand is posted negated.
    let covered = solver.new_constraint_tag();
    for r in 0..num_routes {
        let column: Vec<Var> = (0..num_aircraft).map(|a| allocation[a][r]).collect();
        let capacity: Vec<i32> = (0..num_aircraft).map(|a| capabilities[a][r]).collect();
        let terms = weighted(solver, &capacity, &column, -1);
        solver
            .add_constraint(pumpkin_solver::less_than_or_equals(terms, -demand[r], covered))
            .post();
    }

    // Objective: total cost of the assignment. Its bounds come from the cost
    // table and the largest possible allocation per cell.
    let flat_vars: Vec<Var> = allocation.iter().flatten().copied().collect();
    let flat_costs: Vec<i32> = costs.iter().flatten().copied().collect();
    let lowest: i32 = flat_costs.iter().map(|&c| (c * most).min(0)).sum();
    let highest: i32 = flat_costs.iter().map(|&c| (c * most).max(0)).sum();
    let total_cost = solver.new_bounded_integer(lowest, highest);
    let mut terms = weighted(solver, &flat_costs, &flat_vars, 1);
    terms.push(total_cost.scaled(-1));
    let objective = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(terms, 0, objective))
        .post();

    let mut m = Model::new();
    m.put("allocation", allocation);
    m.minimise(total_cost);
    m
}
