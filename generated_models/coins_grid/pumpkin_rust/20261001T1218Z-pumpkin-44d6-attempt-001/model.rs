// Coins grid: place coins on an n by n grid, c coins in every row and every column
// and at most one per cell, so that the sum of the squared horizontal distances of
// the coins from the main diagonal is as small as possible.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.size("n"); // grid size
    let c = inst.int("c"); // coins in each row and each column

    // x[i][j] is 1 if there is a coin on cell (i, j) and 0 otherwise, so a cell
    // holds at most one coin.
    let x: Vec<Vec<Var>> = (0..n)
        .map(|_| (0..n).map(|_| solver.new_bounded_integer(0, 1)).collect())
        .collect();

    // Every row has exactly c coins.
    let rows = solver.new_constraint_tag();
    for i in 0..n {
        solver
            .add_constraint(pumpkin_solver::equals(x[i].clone(), c, rows))
            .post();
    }

    // Every column has exactly c coins.
    let columns = solver.new_constraint_tag();
    for j in 0..n {
        let column: Vec<Var> = (0..n).map(|i| x[i][j]).collect();
        solver
            .add_constraint(pumpkin_solver::equals(column, c, columns))
            .post();
    }

    // z is the sum over coins of the squared distance (i - j)^2 from the main
    // diagonal. Cells on the diagonal have distance 0, a zero coefficient that
    // Pumpkin cannot take, so they are left out of the sum. z ranges from 0 to
    // the cost of covering every cell.
    let mut terms: Vec<Term> = Vec::new();
    let mut every_cell = 0;
    for i in 0..n {
        for j in 0..n {
            let distance = i as i32 - j as i32;
            let squared = distance * distance;
            every_cell += squared;
            if squared != 0 {
                terms.push(x[i][j].scaled(squared));
            }
        }
    }
    let z = solver.new_bounded_integer(0, every_cell);
    terms.push(z.scaled(-1));
    let cost = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(terms, 0, cost))
        .post();

    let mut m = Model::new();
    m.put("x", x);
    m.put("z", z);
    m.minimise(z);
    m
}
