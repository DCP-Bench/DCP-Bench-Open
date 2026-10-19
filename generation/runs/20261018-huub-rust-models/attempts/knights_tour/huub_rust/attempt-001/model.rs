// Knight's tour: a sequence of knight moves that visits every square of an n x n
// chessboard exactly once, without returning to the starting square. x[i][j] is the
// move number (0..n*n-1) of square (i, j). Board size n is read from the instance.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("n");
    let cells = n * n;
    let max = cells as i64 - 1;

    // The chessboard: x[i][j] is the move number of square (i, j), and every square
    // has a different move number (the move numbers are 0..n*n-1).
    let mut x: Vec<Vec<View<i64>>> = Vec::new();
    for _ in 0..n {
        x.push(m.new_int_decisions(n, 0..=max));
    }
    let flat: Vec<View<i64>> = x.iter().flatten().copied().collect();
    m.unique(flat.clone()).post()?;

    // Move t is made from square pos[t] (numbered row-major as i*n + j). The square
    // visited on move t holds move number t: flat[pos[t]] == t.
    let pos = m.new_int_decisions(cells, 0..=max);
    m.unique(pos.clone()).post()?;
    for (t, p) in pos.iter().enumerate() {
        m.element(flat.clone()).index(*p).result((t as i64).into()).post()?;
    }

    // Row and column of the square visited on each move, looked up from the square index.
    let rows: Vec<i64> = (0..cells).map(|p| (p / n) as i64).collect();
    let cols: Vec<i64> = (0..cells).map(|p| (p % n) as i64).collect();
    let mut row = Vec::new();
    let mut col = Vec::new();
    for p in pos.iter() {
        row.push(m.element(rows.clone()).index(*p).define());
        col.push(m.element(cols.clone()).index(*p).define());
    }

    // Each move is a knight's move: from the square of move t to the square of move t+1,
    // the row and column change by one of the eight (+-1, +-2) or (+-2, +-1) offsets.
    let offsets: Vec<Vec<i64>> = vec![
        vec![1, 2],
        vec![2, 1],
        vec![-1, 2],
        vec![2, -1],
        vec![1, -2],
        vec![-2, 1],
        vec![-1, -2],
        vec![-2, -1],
    ];
    let span = n as i64 - 1;
    for t in 0..cells - 1 {
        let dr = m.new_int_decision(-span..=span);
        let dc = m.new_int_decision(-span..=span);
        m.linear(row[t + 1] - row[t]).eq(dr).post()?;
        m.linear(col[t + 1] - col[t]).eq(dc).post()?;
        m.table(vec![dr, dc]).values(offsets.clone()).post()?;
    }

    let mut out = Out::new();
    out.put("x", x);
    Ok(out)
}
