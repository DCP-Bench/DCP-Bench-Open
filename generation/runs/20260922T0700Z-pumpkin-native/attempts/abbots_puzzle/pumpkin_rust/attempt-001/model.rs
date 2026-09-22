// 100 bushels among 100 people: 3 per man, 2 per woman, half per child,
// with five times as many women as men.
//
// The puzzle statement fixes every number, so the instance carries no fields;
// the constants below are the problem, not one instance of it.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let men = solver.new_bounded_integer(0, 100);
    let women = solver.new_bounded_integer(0, 100);
    let children = solver.new_bounded_integer(0, 100);

    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(
            vec![men.scaled(1), women.scaled(1), children.scaled(1)], 100, tag))
        .post();
    // Doubled to clear the child's half bushel.
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(
            vec![men.scaled(6), women.scaled(4), children.scaled(1)], 200, tag))
        .post();
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(
            vec![men.scaled(5), women.scaled(-1)], 0, tag))
        .post();

    let mut m = Model::new();
    m.put("men", men);
    m.put("women", women);
    m.put("children", children);
    m
}
