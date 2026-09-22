// Twenty people at dinner for twenty dollars.
// The prices and party sizes are the puzzle, so the instance carries no fields.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let grandparents = solver.new_bounded_integer(1, 6);
    let parents = solver.new_bounded_integer(1, 10);
    let children = solver.new_bounded_integer(1, 40);

    // $3, $2 and $0.50 a head, doubled to clear the half dollar.
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(
            vec![grandparents.scaled(6), parents.scaled(4), children.scaled(1)],
            20 * 2,
            tag,
        ))
        .post();
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(
            vec![grandparents, parents, children], 20, tag))
        .post();

    let mut m = Model::new();
    m.put("grandparents", grandparents);
    m.put("parents", parents);
    m.put("children", children);
    m
}
