// Magic sequence: x[0..n-1] with every i occurring exactly x[i] times in the sequence.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.size("n");

    // Each entry lies between 0 and n - 1.
    let x: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, n as i32 - 1)).collect();

    // The number i occurs exactly x[i] times. Pumpkin has no count constraint, so
    // for each i a literal per position says "this position holds i" and the
    // literals are summed into x[i].
    let holds = solver.new_constraint_tag();
    let occurrences = solver.new_constraint_tag();
    for i in 0..n {
        let mut is_i: Vec<Lit> = Vec::new();
        for j in 0..n {
            let flag = solver.new_literal();
            solver
                .add_constraint(pumpkin_solver::equals(vec![x[j].scaled(1)], i as i32, holds))
                .reify(flag);
            is_i.push(flag);
        }
        solver
            .add_constraint(pumpkin_solver::boolean_equals(vec![1; n], is_i, x[i], occurrences))
            .post();
    }

    let mut m = Model::new();
    m.put("x", x);
    m
}
