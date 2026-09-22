// One candy per child at least, more than a lower-rated neighbour, fewest overall.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let ratings = inst.ints("ratings");
    let n = ratings.len();

    let x: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(1, n as i32)).collect();
    let z = solver.new_bounded_integer(1, (n * n) as i32);
    let mut total: Vec<Term> = x.iter().map(|v| v.scaled(1)).collect();
    total.push(z.scaled(-1));
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::equals(total, 0, tag)).post();
    // z >= n, as an upper bound on the negation.
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::less_than_or_equals(
            vec![z.scaled(-1)], -(n as i32), tag))
        .post();

    for i in 1..n {
        let tag = solver.new_constraint_tag();
        if ratings[i - 1] > ratings[i] {
            // x[i-1] > x[i], so x[i] - x[i-1] <= -1.
            solver
                .add_constraint(pumpkin_solver::less_than_or_equals(
                    vec![x[i].scaled(1), x[i - 1].scaled(-1)], -1, tag))
                .post();
        } else if ratings[i - 1] < ratings[i] {
            solver
                .add_constraint(pumpkin_solver::less_than_or_equals(
                    vec![x[i - 1].scaled(1), x[i].scaled(-1)], -1, tag))
                .post();
        }
    }

    let mut m = Model::new();
    m.put("x", x);
    m.put("z", z);
    m.minimise(z);
    m
}
