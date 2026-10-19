// Kakuro: insert a digit from 1 to 9 into each white cell so that the sum of the
// numbers in each entry matches its clue and no digit is duplicated in any entry.
// The output x is an n x n matrix; 0 marks a black (non-white) cell.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.size("n");
    let blanks = inst.matrix("blanks");
    // The blanks are the cells whose output is 0; every other cell is white.
    let mut white = vec![vec![true; n]; n];
    for rc in &blanks {
        white[(rc[0] - 1) as usize][(rc[1] - 1) as usize] = false;
    }

    // Insert a digit from 1 to 9 into each white cell; blank cells are fixed to 0.
    let mut x: Vec<Vec<IntVar>> = Vec::with_capacity(n);
    for r in 0..n {
        let mut row = Vec::with_capacity(n);
        for c in 0..n {
            let v = if white[r][c] {
                IntVar::new(1..=9)
            } else {
                IntVar::new(0..=0)
            };
            row.push(v);
        }
        x.push(row);
    }

    // Each entry is a clue followed by its cells, given as 1-based [row, col] pairs.
    let mut entries: Vec<(i64, Vec<IntVar>)> = Vec::new();
    for entry in inst.get("problem").as_array().expect("problem is a list of entries") {
        let parts = entry.as_array().expect("entry is a list");
        let clue = parts[0].as_i64().expect("clue is an integer");
        let mut cells: Vec<IntVar> = Vec::new();
        for p in &parts[1..] {
            let rc = p.as_array().expect("cell is a pair");
            let r = (rc[0].as_i64().expect("row is an integer") - 1) as usize;
            let c = (rc[1].as_i64().expect("col is an integer") - 1) as usize;
            cells.push(x[r][c].clone());
        }
        entries.push((clue, cells));
    }

    // The sum of the numbers in each entry matches the clue associated with it.
    for (clue, cells) in &entries {
        let mut sum = LinExp::default();
        for v in cells {
            sum += iv(v);
        }
        post(s, sum, Comparator::Equal, *clue)?;
    }

    // No digit is duplicated in any entry.
    for (_, cells) in &entries {
        all_different(s, cells)?;
    }

    let mut out = Out::new();
    out.put("x", &x);
    Ok(out)
}
