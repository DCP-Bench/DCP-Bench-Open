// Five brigands share 200 doubloons, and a reweighted share also totals 200.
// The puzzle fixes every number, so the instance carries no fields of its own.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let x: Vec<Var> = (0..5).map(|_| solver.new_bounded_integer(1, 200)).collect();
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::equals(x.clone(), 200, tag)).post();
    // 6 * (12A + 3B + C) + 3D + 2E == 6 * 200, cleared of fractions.
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(
            vec![x[0].scaled(72), x[1].scaled(18), x[2].scaled(6), x[3].scaled(3), x[4].scaled(2)],
            1200,
            tag,
        ))
        .post();

    let mut m = Model::new();
    for (name, v) in ["A", "B", "C", "D", "E"].iter().zip(&x) {
        m.put(name, *v);
    }
    m
}
