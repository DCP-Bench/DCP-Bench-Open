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

    // Move t is made from square pos[t] (numbered row-major as i*n + j). Every square is
    // visited once, so the squares are all different. The square visited on move t holds
    // move number t: flat[pos[t]] == t.
    let pos = m.new_int_decisions(cells, 0..=max);
    m.unique(pos.clone()).post()?;
    for (t, p) in pos.iter().enumerate() {
        m.element(flat.clone()).index(*p).result((t as i64).into()).post()?;
    }

    // Each move is a knight's move: the square of move t and the square of move t+1 are
    // two squares a knight's move apart. The allowed pairs are listed from the board size.
    let mut knight: Vec<Vec<i64>> = Vec::new();
    let offsets: [(i64, i64); 8] = [(1, 2), (2, 1), (-1, 2), (2, -1), (1, -2), (-2, 1), (-1, -2), (-2, -1)];
    let size = n as i64;
    for r in 0..size {
        for c in 0..size {
            for (dr, dc) in offsets {
                let (r2, c2) = (r + dr, c + dc);
                if r2 >= 0 && r2 < size && c2 >= 0 && c2 < size {
                    knight.push(vec![r * size + c, r2 * size + c2]);
                }
            }
        }
    }
    for t in 0..cells - 1 {
        m.table(vec![pos[t], pos[t + 1]]).values(knight.clone()).post()?;
    }

    let mut out = Out::new();
    out.put("x", x);
    Ok(out)
}
