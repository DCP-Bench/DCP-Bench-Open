// Sudoku: fill a 9x9 grid with the digits 1 to 9 so that each row, each column
// and each 3x3 section contains all the digits. The input grid gives some cells
// as numbers; 0 marks an empty cell. Print the solved grid as grid.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let clues = inst.matrix("input_grid");
    let n = clues.len();
    let b = (n as f64).sqrt().round() as usize; // section side, 3 for a 9x9 grid
    // one fresh variable per cell, with the digits 1 to n
    let mut grid: Vec<Vec<IntVar>> = Vec::new();
    for _ in 0..n {
        let row: Vec<IntVar> = (0..n).map(|_| IntVar::new(1..=(n as i64))).collect();
        grid.push(row);
    }

    // the given numbers of the input grid are fixed
    for r in 0..n {
        for c in 0..n {
            let v = clues[r][c];
            if v != 0 {
                post(s, iv(&grid[r][c]), Comparator::Equal, v)?;
            }
        }
    }

    // each row contains all the digits
    for r in 0..n {
        all_different(s, &grid[r])?;
    }

    // each column contains all the digits
    for c in 0..n {
        let col: Vec<IntVar> = (0..n).map(|r| grid[r][c].clone()).collect();
        all_different(s, &col)?;
    }

    // each 3x3 section contains all the digits
    for br in 0..b {
        for bc in 0..b {
            let mut sec: Vec<IntVar> = Vec::new();
            for r in 0..b {
                for c in 0..b {
                    sec.push(grid[br * b + r][bc * b + c].clone());
                }
            }
            all_different(s, &sec)?;
        }
    }

    let mut out = Out::new();
    out.put("grid", &grid);
    Ok(out)
}
