// Knight's tour on an n x n chessboard (satisfaction problem).
// Output x[r][c] is the move number (0..n*n-1) of the knight on square (r, c).

const KNIGHT_DELTAS: [(i64, i64); 8] = [
    (1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1),
];

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.size("n");
    let total = (n * n) as i64;

    // The description: the tour is represented by integers from 0 to n*n-1.
    let mut x: Vec<Vec<IntVar>> = Vec::new();
    for _ in 0..n {
        let row: Vec<IntVar> = (0..n).map(|_| IntVar::new(0..=total - 1)).collect();
        x.push(row);
    }

    // The description: the knight visits every square exactly once,
    // so the move numbers are all different.
    let flat: Vec<IntVar> = x.iter().flatten().cloned().collect();
    all_different(s, &flat)?;

    // The description: the knight moves from one square to the next by a knight move.
    // If move k is on a square, move k+1 is on one of its knight-move neighbours.
    // With all move numbers distinct, this chains 0, 1, ..., n*n-1 into one tour.
    for r in 0..n {
        for c in 0..n {
            let nbrs: Vec<(usize, usize)> = KNIGHT_DELTAS
                .iter()
                .filter_map(|&(dr, dc)| {
                    let nr = r as i64 + dr;
                    let nc = c as i64 + dc;
                    if nr >= 0 && nc >= 0 && (nr as usize) < n && (nc as usize) < n {
                        Some((nr as usize, nc as usize))
                    } else {
                        None
                    }
                })
                .collect();
            for k in 0..total - 1 {
                let mut cl: Vec<Lit> = Vec::new();
                let here = x[r][c].equals(s, k)?;
                cl.push(lit_of(s, !here)?);
                for &(nr, nc) in &nbrs {
                    let nxt = x[nr][nc].equals(s, k + 1)?;
                    cl.push(lit_of(s, nxt)?);
                }
                s.add_clause(cl)?;
            }
        }
    }

    let mut out = Out::new();
    out.put("x", &x);
    Ok(out)
}
