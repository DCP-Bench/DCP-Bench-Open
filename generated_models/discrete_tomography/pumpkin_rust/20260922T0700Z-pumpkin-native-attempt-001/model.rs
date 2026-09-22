// Reconstruct a 0/1 matrix from its row and column sums.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let row_sums = inst.ints("row_sums");
    let col_sums = inst.ints("col_sums");
    let r = row_sums.len();
    let c = col_sums.len();

    let matrix: Vec<Vec<Var>> = (0..r)
        .map(|_| (0..c).map(|_| solver.new_bounded_integer(0, 1)).collect())
        .collect();
    for i in 0..r {
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::equals(matrix[i].clone(), row_sums[i], tag))
            .post();
    }
    for j in 0..c {
        let column: Vec<Var> = (0..r).map(|i| matrix[i][j]).collect();
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::equals(column, col_sums[j], tag))
            .post();
    }

    let mut m = Model::new();
    m.put("matrix", matrix);
    m
}
