// Futoshiki: fill an n x n grid with the digits 1..n so that every row and every
// column contains each digit once. Some cells hold given digits, and some pairs of
// neighbouring cells carry a "less than" constraint. Output: the completed grid.
// The size n and all givens and inequalities come from the instance.
// Reading of the instance: values[r][c] = 0 is an empty cell, otherwise a given digit.
// lt rows are [r1, c1, r2, c2], 1-based: the digit at (r1, c1) is less than the digit at (r2, c2).

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let values = inst.matrix("values");
    let n = values.len();
    let lt = inst.matrix("lt");

    // Each cell holds a digit from 1 to n.
    let grid: Vec<Vec<IntVar>> = (0..n)
        .map(|_| (0..n).map(|_| IntVar::new(1..=n as i64)).collect())
        .collect();

    // Each row and each column contains each digit 1 to n once.
    for r in 0..n {
        all_different(s, &grid[r])?;
    }
    for c in 0..n {
        let col: Vec<IntVar> = (0..n).map(|r| grid[r][c].clone()).collect();
        all_different(s, &col)?;
    }

    // Some digits may be given at the start.
    for r in 0..n {
        for c in 0..n {
            let v = values[r][c];
            if v != 0 {
                post(s, iv(&grid[r][c]), Comparator::Equal, v)?;
            }
        }
    }

    // Inequality constraints: one square must be lower than its neighbour.
    for k in &lt {
        let (r1, c1, r2, c2) = (
            (k[0] - 1) as usize,
            (k[1] - 1) as usize,
            (k[2] - 1) as usize,
            (k[3] - 1) as usize,
        );
        // grid[r1][c1] < grid[r2][c2]
        let mut e = iv(&grid[r1][c1]);
        e += scaled(&grid[r2][c2], -1);
        post(s, e, Comparator::LessEq, -1)?;
    }

    let mut out = Out::new();
    out.put("grid", &grid);
    Ok(out)
}
