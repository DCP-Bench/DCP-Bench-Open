// Knight's tour: a sequence of knight moves that visits every square of an n x n
// chessboard exactly once, without returning to the starting square. x[i][j] is the
// move number (0..n*n-1) of square (i, j). Board size n is read from the instance.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("n");
    let cells = n * n;
    let dummy = cells;
    let size = n as i64;
    let max = cells as i64 - 1;

    // Knight neighbours of every square, with squares numbered row-major as r*n + c.
    let offsets: [(i64, i64); 8] = [(1, 2), (2, 1), (-1, 2), (2, -1), (1, -2), (-2, 1), (-1, -2), (-2, -1)];
    let mut nbrs: Vec<Vec<i64>> = vec![Vec::new(); cells];
    for r in 0..size {
        for c in 0..size {
            for (dr, dc) in offsets {
                let (r2, c2) = (r + dr, c + dc);
                if r2 >= 0 && r2 < size && c2 >= 0 && c2 < size {
                    nbrs[(r * size + c) as usize].push(r2 * size + c2);
                }
            }
        }
    }

    // The tour is a path through the squares. An extra node closes it into a cycle: the
    // dummy node is followed by the first square and follows the last square. next[i]
    // is the node visited after node i.
    let next = m.new_int_decisions(cells + 1, 0..=(dummy as i64));

    // Knight's tour: a square is followed by a square one knight's move away, or by the
    // dummy node when it is the last square.
    for p in 0..cells {
        let mut allowed: Vec<Vec<i64>> = nbrs[p].iter().map(|&q| vec![q]).collect();
        allowed.push(vec![dummy as i64]);
        m.table(vec![next[p]]).values(allowed).post()?;
    }

    // Visit every square exactly once: the successors form a single cycle through all
    // squares and the dummy node.
    circuit(m, &next)?;

    // Move numbers: the dummy node is move -1, and each square is one move after the
    // square that precedes it. The last square is followed by the dummy node, so its
    // move number is not linked to the dummy's.
    let mv = m.new_int_decisions(cells + 1, -1..=max);
    m.linear(mv[dummy]).eq(-1).post()?;
    for p in 0..=cells {
        let after = m.element(mv.clone()).index(next[p]).define();
        let not_last = m.linear(next[p]).ne(dummy as i64).reify();
        m.linear(after - mv[p]).eq(1).reified_by(not_last).post()?;
    }

    let mut x: Vec<Vec<View<i64>>> = Vec::new();
    for i in 0..n {
        x.push((0..n).map(|j| mv[i * n + j]).collect());
    }
    let mut out = Out::new();
    out.put("x", x);
    Ok(out)
}
