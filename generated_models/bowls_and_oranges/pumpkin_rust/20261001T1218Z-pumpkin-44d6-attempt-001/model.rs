// Bowls and oranges: put m oranges in n bowls on a line, at most one per bowl,
// so that no three oranges are equally spaced.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.int("n"); // number of bowls
    let m_oranges = inst.size("m"); // number of oranges

    // x[i] is the bowl (numbered from 1) holding orange i.
    let x: Vec<Var> = (0..m_oranges).map(|_| solver.new_bounded_integer(1, n)).collect();

    // At most one orange per bowl.
    let distinct = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::all_different(x.clone(), distinct))
        .post();

    // The bowls are listed in ascending order.
    let ascending = solver.new_constraint_tag();
    for i in 1..m_oranges {
        solver
            .add_constraint(pumpkin_solver::less_than_or_equals(
                vec![x[i - 1].scaled(1), x[i].scaled(-1)], 0, ascending))
            .post();
    }

    // No three oranges A, B, C with the distance from A to B equal to the distance
    // from B to C: for i < j < k, x[j] - x[i] != x[k] - x[j], i.e. x[i] - 2 x[j] + x[k] != 0.
    let not_equally_spaced = solver.new_constraint_tag();
    for i in 0..m_oranges {
        for j in (i + 1)..m_oranges {
            for k in (j + 1)..m_oranges {
                solver
                    .add_constraint(pumpkin_solver::not_equals(
                        vec![x[i].scaled(1), x[j].scaled(-2), x[k].scaled(1)],
                        0,
                        not_equally_spaced,
                    ))
                    .post();
            }
        }
    }

    let mut m = Model::new();
    m.put("x", x);
    m
}
