// Climb n stairs in moves of m1..m2, padding the tail with zeros.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.size("n");
    let m1 = inst.int("m1");
    let m2 = inst.int("m2");

    // Each move is 0, or between m1 and m2; a sparse domain says exactly that.
    let allowed: Vec<i32> = std::iter::once(0).chain(m1..=m2).collect();
    let steps: Vec<Var> = (0..n)
        .map(|_| solver.new_sparse_integer(allowed.clone()))
        .collect();
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(steps.clone(), n as i32, tag))
        .post();

    // Once a move is zero every later move is zero, so the zeros are a suffix.
    // Half-reification is enough: the implication only runs one way.
    for i in 1..n {
        let stopped = solver.new_literal();
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::equals(vec![steps[i - 1].scaled(1)], 0, tag))
            .reify(stopped);
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::equals(vec![steps[i].scaled(1)], 0, tag))
            .implied_by(stopped);
    }

    let mut m = Model::new();
    m.put("steps", steps);
    m
}
