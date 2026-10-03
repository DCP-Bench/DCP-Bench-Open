// SEND + MORE = MONEY: assign distinct digits to the letters so that the sum
// holds, with no leading zero on S or M.
//
// The instance has no fields: the three words are the puzzle's own data.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let names = ["s", "e", "n", "d", "m", "o", "r", "y"];
    let x: Vec<Var> = names.iter().map(|_| solver.new_bounded_integer(0, 9)).collect();
    let (s, e, n, d, m, o, r, y) = (x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7]);

    // Each letter is a different digit.
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::all_different(x.clone(), tag)).post();

    // SEND + MORE - MONEY == 0, by place value.
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(
            vec![
                s.scaled(1000), e.scaled(100), n.scaled(10), d.scaled(1),
                m.scaled(1000), o.scaled(100), r.scaled(10), e.scaled(1),
                m.scaled(-10000), o.scaled(-1000), n.scaled(-100), e.scaled(-10), y.scaled(-1),
            ],
            0,
            tag,
        ))
        .post();

    // S and M, the leading letters, are not zero.
    let tag = solver.new_constraint_tag();
    for lead in [s, m] {
        solver.add_constraint(pumpkin_solver::less_than_or_equals(vec![lead.scaled(-1)], -1, tag)).post();
    }

    let mut out = Model::new();
    for (k, name) in names.iter().enumerate() {
        out.put(name, x[k]);
    }
    out
}
