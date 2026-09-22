// Make the exact amount from the available coins, using as few coins as possible.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let amount = inst.int("amount");
    let types = inst.ints("types_of_coins");
    let available = inst.ints("available_coins");
    let n = types.len();

    let most = *available.iter().max().unwrap_or(&0);
    let counts: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, most)).collect();
    let paid: Vec<Term> = (0..n)
        .filter(|&i| types[i] != 0)
        .map(|i| counts[i].scaled(types[i]))
        .collect();
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::equals(paid, amount, tag)).post();
    for i in 0..n {
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::less_than_or_equals(
                vec![counts[i].scaled(1)], available[i], tag))
            .post();
    }

    let used = solver.new_bounded_integer(0, most * n as i32);
    let mut tally: Vec<Term> = counts.iter().map(|v| v.scaled(1)).collect();
    tally.push(used.scaled(-1));
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::equals(tally, 0, tag)).post();

    let mut m = Model::new();
    m.put("coin_counts", counts);
    m.minimise(used);
    m
}
