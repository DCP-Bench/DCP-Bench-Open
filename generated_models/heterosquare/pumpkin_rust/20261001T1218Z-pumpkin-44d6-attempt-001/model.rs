// Heterosquare: fill an n x n square with distinct integers from 1 to n*n so that
// the sums of all rows, all columns and the two diagonals are all different.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.size("n");
    let cells = (n * n) as i32;
    // The reference allows every sum to lie in 1..n^3.
    let top = (n * n * n) as i32;

    let x: Vec<Vec<Var>> = (0..n)
        .map(|_| (0..n).map(|_| solver.new_bounded_integer(1, cells)).collect())
        .collect();
    let row_sums: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(1, top)).collect();
    let col_sums: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(1, top)).collect();
    let diag1 = solver.new_bounded_integer(1, top);
    let diag2 = solver.new_bounded_integer(1, top);

    // All the entries of the square are different.
    let entries = solver.new_constraint_tag();
    let flat: Vec<Var> = x.iter().flatten().copied().collect();
    solver
        .add_constraint(pumpkin_solver::all_different(flat, entries))
        .post();

    // All the row sums, column sums and the two diagonal sums are different.
    let sums_differ = solver.new_constraint_tag();
    let mut all_sums: Vec<Var> = Vec::new();
    all_sums.extend(row_sums.iter().copied());
    all_sums.extend(col_sums.iter().copied());
    all_sums.push(diag1);
    all_sums.push(diag2);
    solver
        .add_constraint(pumpkin_solver::all_different(all_sums, sums_differ))
        .post();

    // Each sum variable equals the sum of the cells on its line, written as
    // (sum of cells) - sum = 0.
    let row_tag = solver.new_constraint_tag();
    for i in 0..n {
        let mut terms: Vec<Term> = (0..n).map(|j| x[i][j].scaled(1)).collect();
        terms.push(row_sums[i].scaled(-1));
        solver
            .add_constraint(pumpkin_solver::equals(terms, 0, row_tag))
            .post();
    }
    let col_tag = solver.new_constraint_tag();
    for j in 0..n {
        let mut terms: Vec<Term> = (0..n).map(|i| x[i][j].scaled(1)).collect();
        terms.push(col_sums[j].scaled(-1));
        solver
            .add_constraint(pumpkin_solver::equals(terms, 0, col_tag))
            .post();
    }
    // The main diagonal runs from the top left to the bottom right.
    let diag_tag = solver.new_constraint_tag();
    let mut terms: Vec<Term> = (0..n).map(|i| x[i][i].scaled(1)).collect();
    terms.push(diag1.scaled(-1));
    solver
        .add_constraint(pumpkin_solver::equals(terms, 0, diag_tag))
        .post();
    // The anti-diagonal runs from the top right to the bottom left.
    let mut terms: Vec<Term> = (0..n).map(|i| x[i][n - i - 1].scaled(1)).collect();
    terms.push(diag2.scaled(-1));
    solver
        .add_constraint(pumpkin_solver::equals(terms, 0, diag_tag))
        .post();

    let mut m = Model::new();
    m.put("x", x);
    m
}
