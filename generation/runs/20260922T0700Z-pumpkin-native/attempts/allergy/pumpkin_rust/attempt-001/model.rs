// Match four friends to their allergy and surname.
// The clues are the puzzle, so the instance carries no fields.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let n = 4;
    // Friends: Debra = 0, Janet = 1, Hugh = 2, Rick = 3.
    let (debra, janet, hugh, rick) = (0, 1, 2, 3);

    // foods[i] is the friend allergic to food i; surnames[i] the friend named i.
    let foods: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, n as i32 - 1)).collect();
    let surnames: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, n as i32 - 1)).collect();
    for group in [&foods, &surnames] {
        let tag = solver.new_constraint_tag();
        solver.add_constraint(pumpkin_solver::all_different(group.clone(), tag)).post();
    }

    let (eggs, mold, nuts, ragweed) = (foods[0], foods[1], foods[2], foods[3]);
    let (baxter, lemon, malone, fleet) = (surnames[0], surnames[1], surnames[2], surnames[3]);

    for (variable, friend) in [(mold, rick), (lemon, hugh), (fleet, hugh),
                               (lemon, janet), (eggs, janet), (mold, janet)] {
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::not_equals(vec![variable.scaled(1)], friend, tag))
            .post();
    }
    // The eggs sufferer is the one surnamed Baxter.
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(
            vec![eggs.scaled(1), baxter.scaled(-1)], 0, tag))
        .post();
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(vec![ragweed.scaled(1)], debra, tag))
        .post();

    let mut m = Model::new();
    m.put("eggs", eggs);
    m.put("mold", mold);
    m.put("nuts", nuts);
    m.put("ragweed", ragweed);
    m.put("baxter", baxter);
    m.put("lemon", lemon);
    m.put("malone", malone);
    m.put("fleet", fleet);
    m
}
