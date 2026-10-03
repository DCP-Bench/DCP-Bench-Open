// Costas array: place n marks on an n-by-n grid, one in each row and one in
// each column, so that the vectors between all pairs of marks are different.
// costas[i] is the column (1..n) of the mark in row i.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.size("n"); // size of the array
    let n_i32 = n as i32;

    // costas[i] is the column of the mark in row i, from 1 to n.
    let costas: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(1, n_i32)).collect();

    // One mark per column: the columns of the rows are all different, so the
    // marks form a permutation.
    let permutation = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::all_different(costas.clone(), permutation))
        .post();

    // The difference triangle. For each distance l between two rows, the
    // differences costas[i + l] - costas[i] of the n - l pairs of rows that far
    // apart are all different; together with the row distance l this makes
    // every vector between two marks different. A difference lies between
    // -(n-1) and n-1.
    let define_diff = solver.new_constraint_tag();
    let distinct_in_line = solver.new_constraint_tag();
    for l in 1..n.saturating_sub(1) {
        let mut line: Vec<Var> = Vec::new();
        for i in 0..(n - l) {
            let d = solver.new_bounded_integer(-(n_i32 - 1), n_i32 - 1);
            solver
                .add_constraint(pumpkin_solver::equals(
                    vec![costas[i + l].scaled(1), costas[i].scaled(-1), d.scaled(-1)],
                    0,
                    define_diff,
                ))
                .post();
            line.push(d);
        }
        solver
            .add_constraint(pumpkin_solver::all_different(line, distinct_in_line))
            .post();
    }

    let mut m = Model::new();
    m.put("costas", costas);
    m
}
