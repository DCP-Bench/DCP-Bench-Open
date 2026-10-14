// Futoshiki: fill a square grid with the numbers 1..size so that every row and
// every column holds each number once, some cells are given, and the listed
// "less than" signs between neighbouring cells hold.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    // values[r][c] is the number given in row r, column c; 0 means not given.
    let values = inst.matrix("values");
    // Each row of lt is [r1, c1, r2, c2] (1-based): grid[r1][c1] < grid[r2][c2].
    let lt = inst.matrix("lt");
    let size = values.len();

    let grid: Vec<Vec<Var>> = (0..size)
        .map(|_| (0..size).map(|_| solver.new_bounded_integer(1, size as i32)).collect())
        .collect();

    // The numbers that are given at the start.
    let given = solver.new_constraint_tag();
    for r in 0..size {
        for c in 0..size {
            if values[r][c] > 0 {
                solver
                    .add_constraint(pumpkin_solver::equals(
                        vec![grid[r][c].scaled(1)], values[r][c], given))
                    .post();
            }
        }
    }

    // Every row holds different numbers.
    let rows_differ = solver.new_constraint_tag();
    for r in 0..size {
        solver
            .add_constraint(pumpkin_solver::all_different(grid[r].clone(), rows_differ))
            .post();
    }

    // Every column holds different numbers.
    let cols_differ = solver.new_constraint_tag();
    for c in 0..size {
        let column: Vec<Var> = (0..size).map(|r| grid[r][c]).collect();
        solver
            .add_constraint(pumpkin_solver::all_different(column, cols_differ))
            .post();
    }

    // Each inequality sign: the first cell is smaller than the second, written
    // as first - second <= -1 because Pumpkin only has the "<=" form.
    let smaller = solver.new_constraint_tag();
    for sign in &lt {
        let first = grid[(sign[0] - 1) as usize][(sign[1] - 1) as usize];
        let second = grid[(sign[2] - 1) as usize][(sign[3] - 1) as usize];
        solver
            .add_constraint(pumpkin_solver::less_than_or_equals(
                vec![first.scaled(1), second.scaled(-1)], -1, smaller))
            .post();
    }

    let mut m = Model::new();
    m.put("grid", grid);
    m
}
