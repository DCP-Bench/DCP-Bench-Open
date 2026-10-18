// Killer sudoku: fill the n x n grid (n = 9) with the numbers 1 to 9.
// Each row, column and nonet contains each number exactly once.
// The sum of all numbers in a cage must match the small number printed in its corner.
// No number appears more than once in a cage.
// Cages come from the instance field "problem": a list of [sum, [[row, col], ...]],
// with 1-based coordinates.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("n");
    let hi = n as i64;

    // The grid of decision variables, x[row][col], 0-based.
    let mut x: Vec<Vec<View<i64>>> = Vec::new();
    for _ in 0..n {
        let mut row: Vec<View<i64>> = Vec::new();
        for _ in 0..n {
            row.push(m.new_int_decision(1..=hi));
        }
        x.push(row);
    }

    // Each row contains each number exactly once.
    // Each column contains each number exactly once.
    for r in 0..n {
        m.unique(x[r].clone()).post()?;
    }
    for c in 0..n {
        let col: Vec<View<i64>> = (0..n).map(|r| x[r][c].clone()).collect();
        m.unique(col).post()?;
    }

    // Each nonet (3 x 3 block) contains each number exactly once.
    let block = 3;
    for br in 0..(n / block) {
        for bc in 0..(n / block) {
            let mut cells: Vec<View<i64>> = Vec::new();
            for r in (br * block)..((br + 1) * block) {
                for c in (bc * block)..((bc + 1) * block) {
                    cells.push(x[r][c].clone());
                }
            }
            m.unique(cells).post()?;
        }
    }

    // The sum of all numbers in a cage must match the small number printed in its corner.
    // No number appears more than once in a cage.
    let cages = inst
        .get("problem")
        .as_array()
        .expect("problem must be an array of cages");
    for cage in cages {
        let parts = cage.as_array().expect("a cage must be [sum, cells]");
        let total = parts[0].as_i64().expect("a cage sum must be an integer");
        let mut cells: Vec<View<i64>> = Vec::new();
        for cell in parts[1].as_array().expect("cage cells must be an array") {
            let rc = cell.as_array().expect("a cell must be [row, col]");
            let r = rc[0].as_i64().expect("a row must be an integer") as usize - 1;
            let c = rc[1].as_i64().expect("a column must be an integer") as usize - 1;
            cells.push(x[r][c].clone());
        }
        m.linear(cells.iter().copied().sum::<IntLinearExp>())
            .eq(total)
            .post()?;
        if cells.len() > 1 {
            m.unique(cells).post()?;
        }
    }

    let mut out = Out::new();
    out.put("x", x);
    Ok(out)
}
