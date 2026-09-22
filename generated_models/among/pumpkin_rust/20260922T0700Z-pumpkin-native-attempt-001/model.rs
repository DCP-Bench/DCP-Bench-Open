// Exactly m of the n variables take a value from v.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.size("n");
    let wanted = inst.int("m");
    let v = inst.ints("v");

    // 0..7 is the domain the problem statement fixes, not an instance field.
    let x: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, 7)).collect();
    let mut hits: Vec<Lit> = Vec::new();
    for i in 0..n {
        for &value in &v {
            // A literal that is true exactly when x[i] takes this value.
            let flag = solver.new_literal();
            let tag = solver.new_constraint_tag();
            solver
                .add_constraint(pumpkin_solver::equals(vec![x[i].scaled(1)], value, tag))
                .reify(flag);
            hits.push(flag);
        }
    }
    let target = solver.new_bounded_integer(wanted, wanted);
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::boolean_equals(
            vec![1; hits.len()], hits, target, tag))
        .post();

    let mut m = Model::new();
    m.put("x", x);
    m
}
