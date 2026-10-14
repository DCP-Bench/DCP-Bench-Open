// Fancy dress: Mr Greenguest owns a green shirt and can buy a green tie ($10), a
// used green hat ($2) and green socks ($12); a guest not dressed by the three
// rules pays an $11 entrance fee. Find the cheapest way for him to take part.
//
// The instance has no fields: the rules and the prices are the puzzle's own
// constants, mirrored from the reference.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let t = solver.new_literal(); // green tie
    let h = solver.new_literal(); // green hat
    let r = solver.new_literal(); // green shirt
    let s = solver.new_literal(); // green socks
    let n = solver.new_literal(); // pays the entrance fee

    // Rule 4: a guest who breaks rules 1-3 pays the fee, so each rule below holds
    // or n is true.
    let rules = solver.new_constraint_tag();
    // 1. A green tie requires a green shirt.
    solver.add_constraint(pumpkin_solver::clause(vec![!t, r, n], rules)).post();
    // 2. Green socks or a green shirt only with a green tie or a green hat.
    solver.add_constraint(pumpkin_solver::clause(vec![!s, t, h, n], rules)).post();
    solver.add_constraint(pumpkin_solver::clause(vec![!r, t, h, n], rules)).post();
    // 3. A green shirt, a green hat, or no green socks requires a green tie.
    solver.add_constraint(pumpkin_solver::clause(vec![!r, t, n], rules)).post();
    solver.add_constraint(pumpkin_solver::clause(vec![!h, t, n], rules)).post();
    solver.add_constraint(pumpkin_solver::clause(vec![s, t, n], rules)).post();

    // The cost: tie $10, hat $2, socks $12, entrance fee $11 (the shirt is owned).
    // Its bound is the sum of all prices.
    let prices = vec![10, 2, 12, 11];
    let cost = solver.new_bounded_integer(0, prices.iter().sum());
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::boolean_equals(prices, vec![t, h, s, n], cost, tag))
        .post();

    let mut m = Model::new();
    m.put("t", t);
    m.put("h", h);
    m.put("r", r);
    m.put("s", s);
    m.put("n", n);
    m.minimise(cost);
    m
}
