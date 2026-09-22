// Three truthful cub scouts, and who among them is guilty.
// The statements are the puzzle, so the instance carries no fields.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let p: Vec<Lit> = (0..3).map(|_| solver.new_literal()).collect();
    let (huey, dewey, louie) = (p[0], p[1], p[2]);

    // Huey: Dewey and Louie are guilty together or not at all.
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(
            vec![dewey.get_integer_variable(), louie.get_integer_variable().scaled(-1)],
            0,
            tag,
        ))
        .post();
    // Dewey: if Huey is guilty, so am I.
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::clause(vec![!huey, dewey], tag)).post();
    // Louie: Dewey and I are not both guilty.
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::boolean_less_than_or_equals(
            vec![1, 1], vec![dewey, louie], 1, tag))
        .post();

    let mut m = Model::new();
    m.put("huey", huey);
    m.put("dewey", dewey);
    m.put("louie", louie);
    m
}
