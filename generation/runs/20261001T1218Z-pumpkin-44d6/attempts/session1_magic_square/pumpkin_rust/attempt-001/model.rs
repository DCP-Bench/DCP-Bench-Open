// Magic square: fill an n x n grid with the different integers 1..n^2 so that
// every row, every column and both diagonals add up to the same magic sum.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.size("n");
    let ni = n as i32;
    // The magic sum is fixed by the problem: n(n^2 + 1)/2, the total 1 + ... + n^2
    // shared equally by the n rows.
    let magic_sum = ni * (ni * ni + 1) / 2;

    let square: Vec<Vec<Var>> = (0..n)
        .map(|_| (0..n).map(|_| solver.new_bounded_integer(1, ni * ni)).collect())
        .collect();

    // All numbers in the magic square are different.
    let tag = solver.new_constraint_tag();
    let flat: Vec<Var> = square.iter().flatten().copied().collect();
    solver.add_constraint(pumpkin_solver::all_different(flat, tag)).post();

    // Each row adds up to the magic sum.
    let rows = solver.new_constraint_tag();
    for i in 0..n {
        solver
            .add_constraint(pumpkin_solver::equals(square[i].clone(), magic_sum, rows))
            .post();
    }
    // Each column adds up to the magic sum.
    let cols = solver.new_constraint_tag();
    for j in 0..n {
        let column: Vec<Var> = (0..n).map(|i| square[i][j]).collect();
        solver
            .add_constraint(pumpkin_solver::equals(column, magic_sum, cols))
            .post();
    }
    // The main diagonal and the other diagonal add up to the magic sum.
    let diagonals = solver.new_constraint_tag();
    let main: Vec<Var> = (0..n).map(|i| square[i][i]).collect();
    let other: Vec<Var> = (0..n).map(|i| square[i][n - 1 - i]).collect();
    solver.add_constraint(pumpkin_solver::equals(main, magic_sum, diagonals)).post();
    solver.add_constraint(pumpkin_solver::equals(other, magic_sum, diagonals)).post();

    let mut m = Model::new();
    m.put("square", square);
    m
}
