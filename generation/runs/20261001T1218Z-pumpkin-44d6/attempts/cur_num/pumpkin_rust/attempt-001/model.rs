// Curious number (Dudeney): 48 plus 1 is a square, and half of 48 plus 1 is a
// square too. Find another number between 1 and 10000 with this peculiarity.
//
// The instance has no fields: the range 1..10000 and the known number 48 are the
// puzzle's own constants, mirrored from the reference.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let top = 10000;
    let peculiar = solver.new_bounded_integer(1, top);
    let a = solver.new_bounded_integer(1, top); // the number plus 1
    let b = solver.new_bounded_integer(1, top); // its square root
    let c = solver.new_bounded_integer(1, top); // half the number
    let d = solver.new_bounded_integer(1, top); // half the number plus 1
    let e = solver.new_bounded_integer(1, top); // its square root

    // 48 is already known.
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::not_equals(vec![peculiar], 48, tag)).post();

    // Adding 1 to the number gives a square.
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(vec![peculiar.scaled(1), a.scaled(-1)], -1, tag))
        .post();
    solver.add_constraint(pumpkin_solver::times(b, b, a, tag)).post();

    // The number is even, and adding 1 to its half gives a square.
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(vec![peculiar.scaled(1), c.scaled(-2)], 0, tag))
        .post();
    solver
        .add_constraint(pumpkin_solver::equals(vec![c.scaled(1), d.scaled(-1)], -1, tag))
        .post();
    solver.add_constraint(pumpkin_solver::times(e, e, d, tag)).post();

    let mut m = Model::new();
    m.put("peculiar", peculiar);
    m
}
