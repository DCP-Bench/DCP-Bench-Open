// Digits 1..8 around a square, each side cell the sum of its two corners.
// The layout is the puzzle itself, so the instance carries no fields.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let n = 8;
    let p: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(1, n as i32)).collect();
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::all_different(p.clone(), tag)).post();

    // reading order: a b c / d e / f g h
    let (a, b, cc, d, e, f, g, h) = (p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7]);
    for (target, left, right) in [(b, a, cc), (d, a, f), (e, cc, h), (g, f, h)] {
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::equals(
                vec![target.scaled(1), left.scaled(-1), right.scaled(-1)], 0, tag))
            .post();
    }

    let mut m = Model::new();
    m.put("positions", p);
    m
}
