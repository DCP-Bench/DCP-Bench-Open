// Perfect square placement: pack squares of given sizes into a big square without
// overlap, the squares' areas adding up to exactly the big square's area.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let base = inst.int("base"); // side length of the large square
    let sides = inst.ints("sides"); // side lengths of the small squares
    let n = sides.len();

    // x_coords[i], y_coords[i]: lower-left corner of square i, counted from 0.
    // A square must lie inside the big square, i.e. coordinate + side <= base,
    // which is the same as capping the domain at base - side.
    let x_coords: Vec<Var> = (0..n).map(|i| solver.new_bounded_integer(0, base - sides[i])).collect();
    let y_coords: Vec<Var> = (0..n).map(|i| solver.new_bounded_integer(0, base - sides[i])).collect();

    // No two squares overlap: for each pair, one is to the left of, to the right
    // of, below or above the other. Each of the four cases gets a literal that
    // implies it, and at least one of the four literals must be true.
    let separation = solver.new_constraint_tag();
    let one_of_four = solver.new_constraint_tag();
    for a in 0..n {
        for b in (a + 1)..n {
            let mut cases: Vec<Lit> = Vec::new();
            // (before, after, side of `before`) for the four cases
            let arrangements = [
                (x_coords[a], x_coords[b], sides[a]), // a left of b
                (x_coords[b], x_coords[a], sides[b]), // b left of a
                (y_coords[a], y_coords[b], sides[a]), // a below b
                (y_coords[b], y_coords[a], sides[b]), // b below a
            ];
            for (before, after, width) in arrangements {
                let flag = solver.new_literal();
                // before + width <= after
                solver
                    .add_constraint(pumpkin_solver::less_than_or_equals(
                        vec![before.scaled(1), after.scaled(-1)], -width, separation))
                    .implied_by(flag);
                cases.push(flag);
            }
            solver
                .add_constraint(pumpkin_solver::clause(cases, one_of_four))
                .post();
        }
    }

    // Implied constraint, added only to speed up search: the squares crossing any
    // vertical line have heights summing to at most base, and likewise for any
    // horizontal line. This is a cumulative resource of capacity base, with each
    // square's extent as both duration and demand.
    let along_x = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::cumulative(
            x_coords.clone(), sides.clone(), sides.clone(), base, along_x))
        .post();
    let along_y = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::cumulative(
            y_coords.clone(), sides.clone(), sides.clone(), base, along_y))
        .post();

    let mut m = Model::new();
    m.put("x_coords", x_coords);
    m.put("y_coords", y_coords);
    m
}
