// Quasigroup completion: complete a partially filled N-by-N Latin square, a
// grid in which each of the numbers 1..N occurs exactly once in every row and
// every column.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.size("N"); // order of the quasigroup
    let start = inst.matrix("start"); // given cells; 0 marks an empty cell

    // puzzle[i][j] is the number in row i, column j, from 1 to N.
    let puzzle: Vec<Vec<Var>> = (0..n)
        .map(|_| (0..n).map(|_| solver.new_bounded_integer(1, n as i32)).collect())
        .collect();

    // The given cells keep their number.
    let given = solver.new_constraint_tag();
    for i in 0..n {
        for j in 0..n {
            if start[i][j] != 0 {
                solver
                    .add_constraint(pumpkin_solver::equals(vec![puzzle[i][j].scaled(1)], start[i][j], given))
                    .post();
            }
        }
    }

    // Each row holds different numbers.
    let rows = solver.new_constraint_tag();
    for i in 0..n {
        solver
            .add_constraint(pumpkin_solver::all_different(puzzle[i].clone(), rows))
            .post();
    }

    // Each column holds different numbers.
    let columns = solver.new_constraint_tag();
    for j in 0..n {
        let column: Vec<Var> = (0..n).map(|i| puzzle[i][j]).collect();
        solver
            .add_constraint(pumpkin_solver::all_different(column, columns))
            .post();
    }

    let mut m = Model::new();
    m.put("puzzle", puzzle);
    m
}
