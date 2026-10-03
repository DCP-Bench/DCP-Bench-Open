// Finding celebrities: at a party, graph[i][j] = 1 means person i knows person
// j. A celebrity is known by everybody and knows only celebrities; at least
// one celebrity is present. Decide who the celebrities are.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let graph = inst.matrix("graph"); // graph[i][j] == 1 when person i knows person j
    let n = graph.len();

    // celebrities[i] is true when person i is a celebrity.
    let celebrities: Vec<Lit> = (0..n).map(|_| solver.new_literal()).collect();
    // num_celebrities is how many celebrities there are, at least 1.
    let num_celebrities = solver.new_bounded_integer(1, n as i32);

    // num_celebrities is the number of celebrities.
    let count = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::boolean_equals(
            vec![1; n], celebrities.clone(), num_celebrities, count))
        .post();

    // Person i is a celebrity exactly when everybody knows i (the column of i
    // adds up to n) and i knows exactly num_celebrities people, which are then
    // the celebrities. Whether everybody knows i is fixed by the instance; the
    // number of people i knows is compared with the variable num_celebrities.
    let definition = solver.new_constraint_tag();
    for i in 0..n {
        let known_by_all = (0..n).map(|j| graph[j][i]).sum::<i32>() == n as i32;
        if known_by_all {
            let knows: i32 = graph[i].iter().sum();
            // celebrities[i] <-> (num_celebrities == knows)
            solver
                .add_constraint(pumpkin_solver::equals(
                    vec![num_celebrities.scaled(1)], knows, definition))
                .reify(celebrities[i]);
        } else {
            // not known by everybody, so not a celebrity
            solver
                .add_constraint(pumpkin_solver::clause(vec![!celebrities[i]], definition))
                .post();
        }
    }

    let mut m = Model::new();
    m.put("celebrities", celebrities);
    m
}
