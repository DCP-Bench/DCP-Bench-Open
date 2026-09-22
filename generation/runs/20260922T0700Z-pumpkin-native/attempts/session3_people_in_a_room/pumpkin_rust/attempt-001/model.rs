// Order thirteen arrivals so the room is never more than 7 women to 3 men.
// The head counts are the puzzle, so the instance carries no fields.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let total_people = 13;
    let num_males = 4;

    // true is a woman, false a man
    let sequence: Vec<Lit> = (0..total_people).map(|_| solver.new_literal()).collect();
    let women = solver.new_bounded_integer(
        total_people as i32 - num_males, total_people as i32 - num_males);
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::boolean_equals(
            vec![1; total_people], sequence.clone(), women, tag))
        .post();

    // After i arrivals: 3 * women <= 7 * men, with men = i - women, so
    // 3 * women <= 7 * (i - women), i.e. 10 * women <= 7 * i.
    for i in 1..total_people {
        let prefix: Vec<Lit> = sequence[..i].to_vec();
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::boolean_less_than_or_equals(
                vec![10; i], prefix, 7 * i as i32, tag))
            .post();
    }

    let mut m = Model::new();
    m.put("sequence", sequence);
    m
}
