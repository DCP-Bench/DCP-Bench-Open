// A permutation of 0..n-1 whose neighbouring differences permute 1..n-1.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.size("n");
    let top = n as i32 - 1;

    let x: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, top)).collect();
    let diffs: Vec<Var> = (0..n - 1).map(|_| solver.new_bounded_integer(1, top)).collect();
    for group in [&x, &diffs] {
        let tag = solver.new_constraint_tag();
        solver.add_constraint(pumpkin_solver::all_different(group.clone(), tag)).post();
    }

    for i in 0..(n - 1) {
        let signed = solver.new_bounded_integer(-top, top);
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::equals(
                vec![x[i + 1].scaled(1), x[i].scaled(-1), signed.scaled(-1)], 0, tag))
            .post();
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::absolute(
                signed.scaled(1), diffs[i].scaled(1), tag))
            .post();
    }

    let mut m = Model::new();
    m.put("x", x);
    m.put("diffs", diffs);
    m
}
