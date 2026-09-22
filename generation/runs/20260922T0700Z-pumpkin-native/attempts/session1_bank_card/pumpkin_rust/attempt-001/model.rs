// A four digit PIN abcd with cd = 3*ab and da = 2*bc, all digits distinct.
// The clues are the puzzle, so the instance carries no fields.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let digits: Vec<Var> = (0..4).map(|_| solver.new_bounded_integer(0, 9)).collect();
    let (a, b, c_digit, d) = (digits[0], digits[1], digits[2], digits[3]);
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::all_different(digits.clone(), tag)).post();

    // 10c + d == 3 * (10a + b)
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(
            vec![c_digit.scaled(10), d.scaled(1), a.scaled(-30), b.scaled(-3)], 0, tag))
        .post();
    // 10d + a == 2 * (10b + c)
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(
            vec![d.scaled(10), a.scaled(1), b.scaled(-20), c_digit.scaled(-2)], 0, tag))
        .post();

    let mut m = Model::new();
    m.put("a", a);
    m.put("b", b);
    m.put("c", c_digit);
    m.put("d", d);
    m
}
