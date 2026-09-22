// Assign every task to a distinct person at least total cost.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let cost = inst.matrix("cost");
    let rows = cost.len();
    let cols = cost[0].len();

    let x: Vec<Vec<Lit>> = (0..rows)
        .map(|_| (0..cols).map(|_| solver.new_literal()).collect())
        .collect();
    let one = solver.new_bounded_integer(1, 1);
    for i in 0..rows {
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::boolean_equals(
                vec![1; cols], x[i].clone(), one, tag))
            .post();
    }
    for j in 0..cols {
        let column: Vec<Lit> = (0..rows).map(|i| x[i][j]).collect();
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::boolean_less_than_or_equals(
                vec![1; rows], column, 1, tag))
            .post();
    }

    // The total is tied to the chosen pairings. Pumpkin's boolean_equals scales
    // each literal by its weight, so a zero cost is dropped rather than passed.
    let ceiling: i32 = cost.iter().flatten().sum();
    let total = solver.new_bounded_integer(0, ceiling);
    let (weights, lits): (Vec<i32>, Vec<Lit>) = (0..rows)
        .flat_map(|i| (0..cols).map(move |j| (i, j)))
        .filter(|&(i, j)| cost[i][j] != 0)
        .map(|(i, j)| (cost[i][j], x[i][j]))
        .unzip();
    let tag = solver.new_constraint_tag();
    if lits.is_empty() {
        solver
            .add_constraint(pumpkin_solver::equals(vec![total.scaled(1)], 0, tag))
            .post();
    } else {
        solver
            .add_constraint(pumpkin_solver::boolean_equals(weights, lits, total, tag))
            .post();
    }

    let mut m = Model::new();
    m.put("x", x);
    m.minimise(total);
    m
}
