// Flow Free: connect matching colours with pipes so that the pairs are joined and
// the whole board is covered. Each colour's pipe is a single path between its two
// clue cells. Pipes never cross or overlap, so every cell carries exactly one colour.
// Output B: the colour of each cell, 1-based.

fn grid_neighbours(r: usize, c: usize, rows: usize, cols: usize) -> Vec<(usize, usize)> {
    let mut v = Vec::new();
    if r > 0 {
        v.push((r - 1, c));
    }
    if r + 1 < rows {
        v.push((r + 1, c));
    }
    if c > 0 {
        v.push((r, c - 1));
    }
    if c + 1 < cols {
        v.push((r, c + 1));
    }
    v
}

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let board = inst.matrix("board");
    let rows = board.len();
    let cols = board[0].len();
    let colours = *board.iter().flatten().max().expect("empty board") as usize;
    let cells = rows * cols;
    let idx = |r: usize, c: usize| r * cols + c;

    // x[cell][k] is true when the cell carries colour k+1.
    let mut x: Vec<Vec<Lit>> = Vec::new();
    for _ in 0..cells {
        let mut row = Vec::new();
        for _ in 0..colours {
            row.push(s.new_lit());
        }
        x.push(row);
    }

    // The clue cells keep their colour.
    for r in 0..rows {
        for c in 0..cols {
            let v = board[r][c];
            if v > 0 {
                s.add_clause([x[idx(r, c)][(v - 1) as usize]])?;
            }
        }
    }

    // Every cell carries exactly one colour.
    for cell in 0..cells {
        let mut e = LinExp::default();
        for &l in &x[cell] {
            e += LinExp::from(l);
        }
        post(s, e, Comparator::Equal, 1)?;
    }

    // Pipe shape: a clue cell has one neighbour of its colour (its pipe end), and any
    // other cell of a colour has exactly two neighbours of that colour (pipe through).
    for r in 0..rows {
        for c in 0..cols {
            let target = if board[r][c] > 0 { 1 } else { 2 };
            for k in 0..colours {
                let mut e = LinExp::default();
                for (nr, nc) in grid_neighbours(r, c, rows, cols) {
                    e += LinExp::from(x[idx(nr, nc)][k]);
                }
                post_if(s, &[x[idx(r, c)][k]], e, Comparator::Equal, target)?;
            }
        }
    }

    // Connectivity: every cell that is not a clue cell has a parent next to it, of
    // the same colour, at a lower level. Levels strictly decrease along parents, so
    // each chain ends at a clue cell of its colour, and no pipe floats free of an end.
    let lvl: Vec<IntVar> = (0..cells)
        .map(|_| IntVar::new(0..=(cells as i64 - 1)))
        .collect();
    for r in 0..rows {
        for c in 0..cols {
            if board[r][c] > 0 {
                continue;
            }
            let cell = idx(r, c);
            let mut parents: Vec<Lit> = Vec::new();
            for (nr, nc) in grid_neighbours(r, c, rows, cols) {
                let n = idx(nr, nc);
                let p = s.new_lit();
                parents.push(p);
                // A parent has the same colour as the cell.
                for k in 0..colours {
                    s.add_clause([!p, !x[cell][k], x[n][k]])?;
                    s.add_clause([!p, x[cell][k], !x[n][k]])?;
                }
                // A parent has a lower level than the cell.
                post_if(
                    s,
                    &[p],
                    iv(&lvl[n]) - iv(&lvl[cell]),
                    Comparator::LessEq,
                    -1,
                )?;
            }
            s.add_clause(parents)?;
        }
    }

    // Output: the colour of each cell as an integer 1..colours.
    let mut b: Vec<Vec<IntVar>> = Vec::new();
    for r in 0..rows {
        let mut row = Vec::new();
        for c in 0..cols {
            let col = IntVar::new(1..=(colours as i64));
            for k in 0..colours {
                post_if(
                    s,
                    &[x[idx(r, c)][k]],
                    iv(&col),
                    Comparator::Equal,
                    (k + 1) as i64,
                )?;
            }
            row.push(col);
        }
        b.push(row);
    }

    let mut out = Out::new();
    out.put("B", &b);
    Ok(out)
}
