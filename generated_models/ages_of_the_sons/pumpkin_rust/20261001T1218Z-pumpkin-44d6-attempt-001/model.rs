// Ages of the sons: the product of the three sons' ages is 36, their sum alone
// does not identify them (another triple with product 36 has the same sum), and
// there is a single oldest son. Give the ages A1 >= A2 >= A3, oldest first.
//
// The instance has no fields: the product 36 and the age range 0..36 are the
// puzzle's own constants, mirrored from the reference.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let product = 36;

    // A1, A2, A3: the true ages, oldest first. B1, B2, B3: a second triple the
    // mathematician cannot tell apart from the first after learning the sum.
    let a: Vec<Var> = (0..3).map(|_| solver.new_bounded_integer(0, product)).collect();
    let b: Vec<Var> = (0..3).map(|_| solver.new_bounded_integer(0, product)).collect();

    // The oldest son is unique ("the oldest son has blue eyes"): A1 > A2 >= A3.
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::less_than_or_equals(vec![a[1].scaled(1), a[0].scaled(-1)], -1, tag))
        .post();
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::less_than_or_equals(vec![a[2].scaled(1), a[1].scaled(-1)], 0, tag))
        .post();

    // The other triple is listed oldest first too: B1 >= B2 >= B3.
    let order_b = solver.new_constraint_tag();
    for i in 0..2 {
        solver
            .add_constraint(pumpkin_solver::less_than_or_equals(vec![b[i + 1].scaled(1), b[i].scaled(-1)], 0, order_b))
            .post();
    }

    // The two triples are different: their oldest ages differ.
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::not_equals(vec![a[0].scaled(1), b[0].scaled(-1)], 0, tag))
        .post();

    // The product of the ages is 36, for both triples. Written as two binary
    // products; the intermediate is bounded by 36 * 36.
    let products = solver.new_constraint_tag();
    for t in [&a, &b] {
        let partial = solver.new_bounded_integer(0, product * product);
        let total = solver.new_bounded_integer(product, product);
        solver.add_constraint(pumpkin_solver::times(t[0], t[1], partial, products)).post();
        solver.add_constraint(pumpkin_solver::times(partial, t[2], total, products)).post();
    }

    // The sum of the ages (the number of windows) is the same for both triples,
    // which is why the mathematician still needed more information.
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(
            vec![a[0].scaled(1), a[1].scaled(1), a[2].scaled(1), b[0].scaled(-1), b[1].scaled(-1), b[2].scaled(-1)],
            0,
            tag,
        ))
        .post();

    let mut m = Model::new();
    m.put("A1", a[0]);
    m.put("A2", a[1]);
    m.put("A3", a[2]);
    m
}
