// Calvin puzzle: take an n by n grid (instance field n) and fill every square
// with the numbers 1..n^2, each used once, following the sequence 1, 2, ..., n^2.
// Output x: the completed grid as a list of lists of integers.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.size("n");
    let cells = n * n;

    // Position of each number: pos[v-1] is the cell index (row * n + col) holding number v.
    let pos: Vec<IntVar> = (0..cells).map(|_| IntVar::new(0..=(cells as i64 - 1))).collect();
    // The grid: x[c] is the number written in cell c, in 1..=n^2.
    let x: Vec<IntVar> = (0..cells).map(|_| IntVar::new(1..=(cells as i64))).collect();

    // Every number has exactly one cell and every cell holds exactly one number.
    // Channel the two views: cell c holds number v if and only if number v sits in cell c.
    for c in 0..cells {
        for v in 1..=cells {
            let ea = x[c].equals(s, v as i64)?;
            let a = lit_of(s, ea)?;
            let eb = pos[v - 1].equals(s, c as i64)?;
            let b = lit_of(s, eb)?;
            s.add_clause([!a, b])?;
            s.add_clause([a, !b])?;
        }
    }
    // All numbers occupy different cells.
    all_different(s, &pos)?;

    // The next number in the sequence is placed either vertically or horizontally,
    // exactly three squares away from the previous number (two squares gap),
    // or diagonally, exactly two squares away from the previous number (one square gap).
    // Allowed (cell, next cell) pairs are listed once and used as a table for each step.
    let mut rows: Vec<Vec<i64>> = Vec::new();
    for a in 0..cells {
        for b in 0..cells {
            let (r1, c1) = ((a / n) as i64, (a % n) as i64);
            let (r2, c2) = ((b / n) as i64, (b % n) as i64);
            let (dr, dc) = ((r2 - r1).abs(), (c2 - c1).abs());
            let straight = (dr == 3 && dc == 0) || (dr == 0 && dc == 3);
            let diagonal = dr == 2 && dc == 2;
            if straight || diagonal {
                rows.push(vec![a as i64, b as i64]);
            }
        }
    }
    for v in 0..cells.saturating_sub(1) {
        let xs = vec![pos[v].clone(), pos[v + 1].clone()];
        table(s, &xs, &rows)?;
    }

    let grid: Vec<Vec<IntVar>> = (0..n)
        .map(|i| (0..n).map(|j| x[i * n + j].clone()).collect())
        .collect();
    let mut out = Out::new();
    out.put("x", &grid);
    Ok(out)
}
