// Rearrange 1..12 on a clock face so no three adjacent numbers exceed 21.
// The clock is the puzzle, so the instance carries no fields.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let n = 12;
    let x: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(1, n as i32)).collect();
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::all_different(x.clone(), tag)).post();

    // 21 is the smallest bound the highest triplet can have, which the problem
    // statement fixes; the reference bounds its triplet variable by it.
    for i in 0..n {
        let triplet = vec![x[i], x[(i + n - 1) % n], x[(i + n - 2) % n]];
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::less_than_or_equals(triplet, 21, tag))
            .post();
    }

    let mut m = Model::new();
    m.put("x", x);
    m
}
