// Put each person in a free interview slot, one person per slot.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let free = inst.matrix("m");
    let n = free.len();

    let x: Vec<Vec<Lit>> = (0..n)
        .map(|_| (0..n).map(|_| solver.new_literal()).collect())
        .collect();
    let one = solver.new_bounded_integer(1, 1);
    for i in 0..n {
        // The chosen slot must be one this person is free for. The row is 0/1,
        // and a zero weight would divide by zero inside Pumpkin, so the busy
        // slots are dropped rather than weighted.
        let (weights, lits): (Vec<i32>, Vec<Lit>) = free[i]
            .iter()
            .zip(&x[i])
            .filter(|(&w, _)| w != 0)
            .map(|(&w, &l)| (w, l))
            .unzip();
        let tag = solver.new_constraint_tag();
        if lits.is_empty() {
            // Nobody is free at any slot, so the count can never reach one.
            solver
                .add_constraint(pumpkin_solver::equals(vec![one.scaled(1)], 0, tag))
                .post();
        } else {
            solver
                .add_constraint(pumpkin_solver::boolean_equals(weights, lits, one, tag))
                .post();
        }

        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::boolean_equals(
                vec![1; n], x[i].clone(), one, tag))
            .post();
        let column: Vec<Lit> = (0..n).map(|j| x[j][i]).collect();
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::boolean_equals(vec![1; n], column, one, tag))
            .post();
    }

    let mut m = Model::new();
    m.put("x", x);
    m
}
