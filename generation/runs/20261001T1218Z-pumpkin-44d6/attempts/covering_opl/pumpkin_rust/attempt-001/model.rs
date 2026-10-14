// Covering: hire a set of workers so that every task has at least one qualified
// hired worker, at the smallest total hiring cost.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let cost = inst.ints("Cost"); // hiring cost of each worker
    let qualified = inst.matrix("Qualified"); // workers (1-based) able to do each task
    let nb_workers = cost.len();

    // workers[w] is true when worker w is hired.
    let workers: Vec<Lit> = (0..nb_workers).map(|_| solver.new_literal()).collect();

    // total_cost is the cost of hiring the selected workers. Its upper bound is
    // the cost of hiring everybody (the reference allows nb_workers times that,
    // which is looser than needed).
    let ceiling: i32 = cost.iter().sum();
    let total_cost = solver.new_bounded_integer(0, ceiling);

    // total_cost == sum(workers * cost). Zero-cost workers are dropped from the
    // sum because Pumpkin cannot take a zero coefficient.
    let mut terms: Vec<Term> = (0..nb_workers)
        .filter(|&w| cost[w] != 0)
        .map(|w| workers[w].get_integer_variable().scaled(cost[w]))
        .collect();
    terms.push(total_cost.scaled(-1));
    let price = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(terms, 0, price))
        .post();

    // Every task needs at least one of its qualified workers to be hired.
    // The instance numbers workers from 1, so index c - 1.
    let covered = solver.new_constraint_tag();
    for task in &qualified {
        let candidates: Vec<Lit> = task.iter().map(|&c| workers[(c - 1) as usize]).collect();
        solver
            .add_constraint(pumpkin_solver::clause(candidates, covered))
            .post();
    }

    let mut m = Model::new();
    m.put("total_cost", total_cost);
    m.put("workers", workers);
    m.minimise(total_cost);
    m
}
