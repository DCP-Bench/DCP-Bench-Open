// Traffic lights: a four-way junction has four vehicle lights V1..V4 and four
// pedestrian lights P1..P4; give every light a state so that, for each pair of
// neighbouring roads, the combination (V_i, P_i, V_(i+1), P_(i+1)) is one of
// the safe ones listed.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    // Safe combinations of (V_i, P_i, V_next, P_next), one row per combination.
    let allowed_tuples = inst.matrix("allowed_tuples");

    // Vehicle light states: 0 red, 1 red-yellow, 2 green, 3 yellow (the problem
    // statement fixes these). Pedestrian light states: 0 red, 1 green.
    let vehicle: Vec<Var> = (0..4).map(|_| solver.new_bounded_integer(0, 3)).collect();
    let pedestrian: Vec<Var> = (0..4).map(|_| solver.new_bounded_integer(0, 1)).collect();

    // Each junction i pairs its own lights with those of the next road round the
    // junction (road 4 is followed by road 1), and that combination of four
    // light states must be an allowed tuple.
    let safe = solver.new_constraint_tag();
    for i in 0..4 {
        let next = (i + 1) % 4;
        let scope = vec![vehicle[i], pedestrian[i], vehicle[next], pedestrian[next]];
        solver
            .add_constraint(pumpkin_solver::table(scope, allowed_tuples.clone(), safe))
            .post();
    }

    // lights lists the vehicle lights V1..V4 and then the pedestrian lights P1..P4.
    let mut lights: Vec<Var> = vehicle.clone();
    lights.extend(pedestrian.iter());

    let mut m = Model::new();
    m.put("lights", lights);
    m
}
