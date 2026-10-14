// Sudoku: complete the grid so that every row, column and 3x3 block contains
// each of the digits 1..9 once, keeping the digits already given.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    // input_grid[r][c] is the given digit, or 0 for an empty cell.
    let given = inst.matrix("input_grid");
    // The grid is 9 x 9 with 3 x 3 blocks, as the problem fixes; the side and
    // block size are read off the instance grid (block = square root of side).
    let n = given.len();
    let mut block = 1;
    while (block + 1) * (block + 1) <= n {
        block += 1;
    }

    let grid: Vec<Vec<Var>> = (0..n)
        .map(|_| (0..n).map(|_| solver.new_bounded_integer(1, n as i32)).collect())
        .collect();

    // The given cells keep their digits.
    let clues = solver.new_constraint_tag();
    for r in 0..n {
        for c in 0..n {
            if given[r][c] != 0 {
                solver
                    .add_constraint(pumpkin_solver::equals(vec![grid[r][c].scaled(1)], given[r][c], clues))
                    .post();
            }
        }
    }

    // Each row has different digits.
    let rows = solver.new_constraint_tag();
    for r in 0..n {
        solver.add_constraint(pumpkin_solver::all_different(grid[r].clone(), rows)).post();
    }
    // Each column has different digits.
    let cols = solver.new_constraint_tag();
    for c in 0..n {
        let column: Vec<Var> = (0..n).map(|r| grid[r][c]).collect();
        solver.add_constraint(pumpkin_solver::all_different(column, cols)).post();
    }
    // Each block has different digits.
    let blocks = solver.new_constraint_tag();
    for br in (0..n).step_by(block) {
        for bc in (0..n).step_by(block) {
            let cells: Vec<Var> = (br..br + block)
                .flat_map(|r| (bc..bc + block).map(move |c| (r, c)))
                .map(|(r, c)| grid[r][c])
                .collect();
            solver.add_constraint(pumpkin_solver::all_different(cells, blocks)).post();
        }
    }

    let mut m = Model::new();
    m.put("grid", grid);
    m
}
