// Sell the mix of packages that earns most without overbooking any leg.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let seats = inst.ints("available_seats");
    let demand = inst.ints("demand");
    let revenue = inst.ints("revenue");
    let delta = inst.matrix("delta");
    let packages = demand.len();
    let legs = seats.len();

    let ceiling = *demand.iter().max().unwrap_or(&0);
    let sell: Vec<Var> = (0..packages).map(|_| solver.new_bounded_integer(0, ceiling)).collect();
    for i in 0..packages {
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::less_than_or_equals(
                vec![sell[i].scaled(1)], demand[i], tag))
            .post();
    }
    for j in 0..legs {
        // A package that does not use this leg carries coefficient zero.
        let uses: Vec<Term> = (0..packages)
            .filter(|&i| delta[i][j] != 0)
            .map(|i| sell[i].scaled(delta[i][j]))
            .collect();
        if uses.is_empty() {
            continue;
        }
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::less_than_or_equals(uses, seats[j], tag))
            .post();
    }

    let top: i32 = (0..packages).map(|i| revenue[i] * demand[i]).sum();
    let earned = solver.new_bounded_integer(0, top);
    let mut takings: Vec<Term> = (0..packages)
        .filter(|&i| revenue[i] != 0)
        .map(|i| sell[i].scaled(revenue[i]))
        .collect();
    takings.push(earned.scaled(-1));
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::equals(takings, 0, tag)).post();

    let mut m = Model::new();
    m.put("packages_to_sell", sell);
    m.put("max_revenue", earned);
    m.maximise(earned);
    m
}
