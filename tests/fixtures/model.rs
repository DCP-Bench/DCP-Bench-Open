fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.int("n");
    let x = solver.new_bounded_integer(0, n);
    let y = solver.new_bounded_integer(0, n);
    let mut m = Model::new();
    m.put("x", x);
    m.put("y", y);
    let tag = solver.new_constraint_tag();
    if inst.flag("optimize") {
        solver
            .add_constraint(pumpkin_solver::less_than_or_equals(
                vec![x.scaled(-1), y.scaled(-1)], -n, tag))
            .post();
        let total = solver.new_bounded_integer(0, 2 * n);
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::equals(
                vec![x.scaled(1), y.scaled(1), total.scaled(-1)], 0, tag))
            .post();
        m.minimise(total);
    } else {
        solver
            .add_constraint(pumpkin_solver::equals(
                vec![x.scaled(1), y.scaled(1)], n, tag))
            .post();
    }
    m
}
