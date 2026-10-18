// Futoshiki: fill an n x n grid with the digits 1 to n so that every row and every
// column contains each digit exactly once. Some squares are given a digit at the start,
// and some pairs of neighbouring squares carry an inequality sign. Output: the completed
// grid as a list of lists of integers.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    // the board size and the givens come from the instance; 0 marks an empty square
    let values = inst.matrix("values");
    let n = values.len();
    // each inequality: the square (r1, c1) holds a smaller digit than (r2, c2), 1-based
    let lt = inst.matrix("lt");

    // the squares: each holds one digit from 1 to n, and a given digit fixes its square
    let mut grid = Vec::new();
    for r in 0..n {
        let mut row = Vec::new();
        for c in 0..n {
            let given = values[r][c];
            let x = if given != 0 {
                m.new_int_decision(given..=given)
            } else {
                m.new_int_decision(1..=n as i64)
            };
            row.push(x);
        }
        grid.push(row);
    }

    // every row contains each digit once
    for r in 0..n {
        m.unique(grid[r].clone()).post()?;
    }

    // every column contains each digit once
    for c in 0..n {
        let col: Vec<_> = (0..n).map(|r| grid[r][c].clone()).collect();
        m.unique(col).post()?;
    }

    // the inequality signs between neighbouring squares must be honoured:
    // the square (r1, c1) is less than the square (r2, c2)
    for cl in &lt {
        let a = grid[(cl[0] - 1) as usize][(cl[1] - 1) as usize].clone();
        let b = grid[(cl[2] - 1) as usize][(cl[3] - 1) as usize].clone();
        m.linear(a - b).le(-1).post()?;
    }

    let mut out = Out::new();
    out.put("grid", grid);
    Ok(out)
}
