// Match participants to cars they want, as many matches as possible.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let possible = inst.matrix("possible_assignments");
    let participants = possible.len();
    let cars = possible[0].len();

    let assignments: Vec<Vec<Lit>> = (0..participants)
        .map(|_| (0..cars).map(|_| solver.new_literal()).collect())
        .collect();
    for i in 0..participants {
        for j in 0..cars {
            if possible[i][j] == 0 {
                let tag = solver.new_constraint_tag();
                solver
                    .add_constraint(pumpkin_solver::equals(
                        vec![assignments[i][j].scaled(1)], 0, tag))
                    .post();
            }
        }
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::boolean_less_than_or_equals(
                vec![1; cars], assignments[i].clone(), 1, tag))
            .post();
    }
    for j in 0..cars {
        let column: Vec<Lit> = (0..participants).map(|i| assignments[i][j]).collect();
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::boolean_less_than_or_equals(
                vec![1; participants], column, 1, tag))
            .post();
    }

    let flat: Vec<Lit> = assignments.iter().flatten().copied().collect();
    let matched = solver.new_bounded_integer(0, flat.len() as i32);
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::boolean_equals(
            vec![1; flat.len()], flat, matched, tag))
        .post();

    let mut m = Model::new();
    m.put("assignments", assignments);
    m.maximise(matched);
    m
}
