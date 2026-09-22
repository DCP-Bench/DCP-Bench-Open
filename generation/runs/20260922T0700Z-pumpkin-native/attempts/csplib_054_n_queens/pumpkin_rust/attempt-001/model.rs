// Place n queens so that no two share a row, column or diagonal.
// Columns are 1-indexed, as the reference declares them.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.size("n");
    let queens: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(1, n as i32)).collect();
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::all_different(queens.clone(), tag)).post();
    // The two diagonal all-differents, written as the pairwise disequalities
    // Pumpkin would decompose them into anyway.
    for i in 0..n {
        for j in (i + 1)..n {
            let d = (j - i) as i32;
            for rhs in [d, -d] {
                let tag = solver.new_constraint_tag();
                solver
                    .add_constraint(pumpkin_solver::not_equals(
                        vec![queens[i].scaled(1), queens[j].scaled(-1)], rhs, tag))
                    .post();
            }
        }
    }

    let mut m = Model::new();
    m.put("queens", queens);
    m
}
