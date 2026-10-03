// Wolf, goat and cabbage: a farmer must ferry a wolf, a goat and a cabbage
// across a river over a given number of stages. The boat crosses at every stage
// and carries at most one item; the wolf may not be left with the goat, nor the
// goat with the cabbage, on the shore where the boat is not.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let stage = inst.size("stage");

    // x_pos[i] is true when x is on the destination shore at stage i.
    let wolf_pos: Vec<Lit> = (0..stage).map(|_| solver.new_literal()).collect();
    let goat_pos: Vec<Lit> = (0..stage).map(|_| solver.new_literal()).collect();
    let cabbage_pos: Vec<Lit> = (0..stage).map(|_| solver.new_literal()).collect();
    let boat_pos: Vec<Lit> = (0..stage).map(|_| solver.new_literal()).collect();

    // Initially everything is on the starting shore; finally everything is on
    // the destination shore.
    let ends = solver.new_constraint_tag();
    let last = stage - 1;
    solver
        .add_constraint(pumpkin_solver::conjunction(
            vec![!boat_pos[0], !wolf_pos[0], !goat_pos[0], !cabbage_pos[0]], ends))
        .post();
    solver
        .add_constraint(pumpkin_solver::conjunction(
            vec![boat_pos[last], wolf_pos[last], goat_pos[last], cabbage_pos[last]], ends))
        .post();

    // The boat changes shore at every stage.
    let crossing = solver.new_constraint_tag();
    for i in 1..stage {
        solver
            .add_constraint(pumpkin_solver::clause(vec![boat_pos[i], boat_pos[i - 1]], crossing))
            .post();
        solver
            .add_constraint(pumpkin_solver::clause(vec![!boat_pos[i], !boat_pos[i - 1]], crossing))
            .post();
    }

    // The wolf and the goat are not left together without the boat: if they are
    // on the same shore, the boat is there too. Likewise the goat and the cabbage.
    let unattended = solver.new_constraint_tag();
    for i in 0..stage {
        for (a, b) in [(wolf_pos[i], goat_pos[i]), (goat_pos[i], cabbage_pos[i])] {
            solver
                .add_constraint(pumpkin_solver::clause(vec![!a, !b, boat_pos[i]], unattended))
                .post();
            solver
                .add_constraint(pumpkin_solver::clause(vec![a, b, !boat_pos[i]], unattended))
                .post();
        }
    }

    // At most one of wolf, goat and cabbage changes shore between consecutive
    // stages. moved is forced true whenever the item's position differs; being
    // forced only upwards suffices, since a true value can only tighten the
    // at-most-one.
    let one_item = solver.new_constraint_tag();
    for i in 0..stage.saturating_sub(1) {
        let mut moved: Vec<Lit> = Vec::new();
        for pos in [&wolf_pos, &goat_pos, &cabbage_pos] {
            let m = solver.new_literal();
            solver
                .add_constraint(pumpkin_solver::clause(vec![!pos[i], pos[i + 1], m], one_item))
                .post();
            solver
                .add_constraint(pumpkin_solver::clause(vec![pos[i], !pos[i + 1], m], one_item))
                .post();
            moved.push(m);
        }
        solver
            .add_constraint(pumpkin_solver::boolean_less_than_or_equals(vec![1; 3], moved, 1, one_item))
            .post();
    }

    let mut m = Model::new();
    m.put("wolf_pos", wolf_pos);
    m.put("goat_pos", goat_pos);
    m.put("cabbage_pos", cabbage_pos);
    m.put("boat_pos", boat_pos);
    m
}
