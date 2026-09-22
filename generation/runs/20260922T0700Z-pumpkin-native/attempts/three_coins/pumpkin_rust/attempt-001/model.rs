// Flip one coin per move so that all coins end up alike.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let init = inst.ints("init");
    let num_moves = inst.size("num_moves");
    let n = init.len();

    let steps: Vec<Vec<Lit>> = (0..num_moves + 1)
        .map(|_| (0..n).map(|_| solver.new_literal()).collect())
        .collect();
    for j in 0..n {
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::equals(
                vec![steps[0][j].get_integer_variable()], init[j], tag))
            .post();
    }
    // Exactly one coin differs between consecutive rows, so n - 1 stay the same.
    let unchanged = solver.new_bounded_integer(n as i32 - 1, n as i32 - 1);
    for row in 1..=num_moves {
        let mut same: Vec<Lit> = Vec::new();
        for j in 0..n {
            let flag = solver.new_literal();
            let tag = solver.new_constraint_tag();
            solver
                .add_constraint(pumpkin_solver::equals(
                    vec![
                        steps[row][j].get_integer_variable(),
                        steps[row - 1][j].get_integer_variable().scaled(-1),
                    ],
                    0,
                    tag,
                ))
                .reify(flag);
            same.push(flag);
        }
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::boolean_equals(
                vec![1; n], same, unchanged, tag))
            .post();
    }
    // The last row is all heads or all tails.
    let last = solver.new_bounded_integer(0, n as i32);
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::boolean_equals(
            vec![1; n], steps[num_moves].clone(), last, tag))
        .post();
    let mut alike: Vec<Lit> = Vec::new();
    for value in [0, n as i32] {
        let flag = solver.new_literal();
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::equals(vec![last.scaled(1)], value, tag))
            .reify(flag);
        alike.push(flag);
    }
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::clause(alike, tag)).post();

    let mut m = Model::new();
    m.put("steps", steps);
    m
}
