// Eighteen holes of par 3, 4 or 5 adding up to a par-72 course.
// The course specification is the puzzle, so the instance carries no fields.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let num_holes = 18;
    let total_length = 72;

    let holes: Vec<Var> = (0..num_holes).map(|_| solver.new_bounded_integer(3, 5)).collect();
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(holes.clone(), total_length, tag))
        .post();

    let mut m = Model::new();
    m.put("holes", holes);
    m
}
