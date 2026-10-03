// Kakuro: put a digit 1..9 in every white cell so that the digits of each entry
// add up to the entry's clue and no digit repeats within an entry. Blank cells
// hold 0.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.size("n");
    // blanks[b] = [row, col] (1-based) of a blank cell.
    let blanks = inst.matrix("blanks");
    // problem[p] = [clue, [row, col], [row, col], ...] (1-based). Entries have
    // different lengths, so the field is ragged and is read from the raw JSON.
    let entries: Vec<(i32, Vec<(usize, usize)>)> = inst
        .get("problem")
        .as_array()
        .expect("problem: expected an array of entries")
        .iter()
        .map(|entry| {
            let items = entry.as_array().expect("problem entry: expected an array");
            let clue = items[0].as_i64().expect("problem entry: clue must be an integer") as i32;
            let cells = items[1..]
                .iter()
                .map(|cell| {
                    let rc = cell.as_array().expect("problem cell: expected [row, col]");
                    (
                        rc[0].as_i64().unwrap() as usize - 1,
                        rc[1].as_i64().unwrap() as usize - 1,
                    )
                })
                .collect();
            (clue, cells)
        })
        .collect();

    // x[i][j] is the digit in row i, column j, or 0 for a blank cell.
    let x: Vec<Vec<Var>> = (0..n)
        .map(|_| (0..n).map(|_| solver.new_bounded_integer(0, 9)).collect())
        .collect();

    // The blank cells hold 0.
    let blank = solver.new_constraint_tag();
    for b in &blanks {
        let cell = x[(b[0] - 1) as usize][(b[1] - 1) as usize];
        solver
            .add_constraint(pumpkin_solver::equals(vec![cell.scaled(1)], 0, blank))
            .post();
    }

    let positive = solver.new_constraint_tag();
    let sums = solver.new_constraint_tag();
    let distinct = solver.new_constraint_tag();
    for (clue, cells) in &entries {
        let vars: Vec<Var> = cells.iter().map(|&(i, j)| x[i][j]).collect();
        // Every cell of an entry holds a digit of at least 1 (written as -x <= -1).
        for &v in &vars {
            solver
                .add_constraint(pumpkin_solver::less_than_or_equals(vec![v.scaled(-1)], -1, positive))
                .post();
        }
        // The digits of the entry add up to its clue.
        solver
            .add_constraint(pumpkin_solver::equals(vars.clone(), *clue, sums))
            .post();
        // No digit repeats within the entry.
        solver
            .add_constraint(pumpkin_solver::all_different(vars, distinct))
            .post();
    }

    let mut m = Model::new();
    m.put("x", x);
    m
}
