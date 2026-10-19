// Hidato puzzle on an N x N grid (N taken from the instance).
// Hidato Puzzles start semi-filled with numbered tiles. Connect the numbers together to win.
// Fill in the empty cells with the numbers that complete the puzzle.
// Output x: the solved grid as a list of lists of integers.

fn nbrs(i: usize, j: usize, n: usize) -> Vec<(usize, usize)> {
    let mut out = Vec::new();
    for di in -1i64..=1 {
        for dj in -1i64..=1 {
            if di == 0 && dj == 0 {
                continue;
            }
            let (a, b) = (i as i64 + di, j as i64 + dj);
            if a >= 0 && b >= 0 && a < n as i64 && b < n as i64 {
                out.push((a as usize, b as usize));
            }
        }
    }
    out
}

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let puzzle = inst.matrix("puzzle");
    let n = puzzle.len();
    let total = (n * n) as i64;

    // Every cell holds one integer in 1..=N*N.
    let mut cell: Vec<Vec<IntVar>> = Vec::with_capacity(n);
    for _ in 0..n {
        let mut row = Vec::with_capacity(n);
        for _ in 0..n {
            row.push(IntVar::new(1..=total));
        }
        cell.push(row);
    }

    // Equality literal eq[c][k-1] <-> cell c holds value k.
    let mut eq: Vec<Vec<Lit>> = Vec::with_capacity(n * n);
    for i in 0..n {
        for j in 0..n {
            let mut lits = Vec::with_capacity(total as usize);
            for k in 1..=total {
                let b = cell[i][j].equals(&mut *s, k)?;
                lits.push(lit_of(s, b)?);
            }
            eq.push(lits);
        }
    }

    // Fill in the empty cells with the numbers that complete the puzzle.
    // Each number 1..N*N appears in exactly one cell.
    let flat: Vec<IntVar> = cell.iter().flatten().cloned().collect();
    all_different(s, &flat)?;

    // Hidato Puzzles start semi-filled with numbered tiles.
    for i in 0..n {
        for j in 0..n {
            let g = puzzle[i][j];
            if g > 0 {
                s.add_clause(vec![eq[i * n + j][(g - 1) as usize]])?;
            }
        }
    }

    // Consecutive number must touch horizontally, vertically, or diagonally.
    // If a cell holds k, one of its neighbours holds k+1.
    for k in 1..total {
        for i in 0..n {
            for j in 0..n {
                let mut clause = vec![!eq[i * n + j][(k - 1) as usize]];
                for (a, b) in nbrs(i, j, n) {
                    clause.push(eq[a * n + b][k as usize]);
                }
                s.add_clause(clause)?;
            }
        }
    }

    // The numbers must be in increasing order.
    // If a cell holds k (k >= 2), one of its neighbours holds k-1.
    for k in 2..=total {
        for i in 0..n {
            for j in 0..n {
                let mut clause = vec![!eq[i * n + j][(k - 1) as usize]];
                for (a, b) in nbrs(i, j, n) {
                    clause.push(eq[a * n + b][(k - 2) as usize]);
                }
                s.add_clause(clause)?;
            }
        }
    }

    let mut out = Out::new();
    out.put("x", &cell);
    Ok(out)
}
