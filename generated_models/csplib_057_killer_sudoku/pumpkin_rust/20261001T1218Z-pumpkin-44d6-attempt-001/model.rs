// Killer sudoku: fill an n-by-n grid with the numbers 1..n so that every row,
// column and 3-by-3 box holds each number once, and every cage (a group of
// cells) holds distinct numbers adding up to the cage's total.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.size("n"); // grid size, 9 in a standard puzzle
    let n_i32 = n as i32;
    // problem is a list of cages, each [total, [[row, col], ...]] with rows and
    // columns counted from 1. The entries mix a number and a list of pairs, so
    // they are read from the raw JSON.
    let cages_json = inst
        .get("problem")
        .as_array()
        .expect("instance field problem: expected an array of cages");

    // x[r][c] is the number in the cell at row r, column c, from 1 to n.
    let x: Vec<Vec<Var>> = (0..n)
        .map(|_| (0..n).map(|_| solver.new_bounded_integer(1, n_i32)).collect())
        .collect();

    // All numbers in a row are different.
    let rows = solver.new_constraint_tag();
    for r in 0..n {
        solver
            .add_constraint(pumpkin_solver::all_different(x[r].clone(), rows))
            .post();
    }

    // All numbers in a column are different.
    let columns = solver.new_constraint_tag();
    for c in 0..n {
        let column: Vec<Var> = (0..n).map(|r| x[r][c]).collect();
        solver
            .add_constraint(pumpkin_solver::all_different(column, columns))
            .post();
    }

    // All numbers in a 3-by-3 box are different (the box size 3 is part of the
    // sudoku rules; the reference fixes it too).
    let boxes = solver.new_constraint_tag();
    for band in 0..(n / 3) {
        for stack in 0..(n / 3) {
            let cells: Vec<Var> = (band * 3..band * 3 + 3)
                .flat_map(|r| (stack * 3..stack * 3 + 3).map(move |c| (r, c)))
                .map(|(r, c)| x[r][c])
                .collect();
            solver
                .add_constraint(pumpkin_solver::all_different(cells, boxes))
                .post();
        }
    }

    // Each cage: its cells add up to the cage total, and no number appears twice in it.
    let totals = solver.new_constraint_tag();
    let cage_distinct = solver.new_constraint_tag();
    for cage in cages_json {
        let total = cage[0].as_i64().expect("cage total must be an integer") as i32;
        let cells: Vec<Var> = cage[1]
            .as_array()
            .expect("cage cells must be an array")
            .iter()
            .map(|cell| {
                let row = cell[0].as_i64().expect("cage cell row") as usize;
                let col = cell[1].as_i64().expect("cage cell column") as usize;
                x[row - 1][col - 1] // the instance counts from 1
            })
            .collect();
        let terms: Vec<Term> = cells.iter().map(|v| v.scaled(1)).collect();
        solver
            .add_constraint(pumpkin_solver::equals(terms, total, totals))
            .post();
        solver
            .add_constraint(pumpkin_solver::all_different(cells, cage_distinct))
            .post();
    }

    let mut m = Model::new();
    m.put("x", x);
    m
}
