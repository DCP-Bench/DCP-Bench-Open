// N-puzzle: sliding tiles on a k x k grid, tiles 0..k*k-1 with 0 the blank.
// Find N_STEPS boards, the first equal to puzzle_start and the last to puzzle_end.
// Each step moves one tile into the blank, so consecutive boards always differ.
// Output "steps": N_STEPS boards of shape k x k.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let start = inst.matrix("puzzle_start");
    let end = inst.matrix("puzzle_end");
    let k = start.len();
    let cells = k * k;
    let n_steps = inst.int("N_STEPS") as usize;
    let max_v = cells as i64 - 1;

    // board[t][c] is the tile at cell c = row * k + col at step t.
    let mut board: Vec<Vec<IntVar>> = Vec::with_capacity(n_steps);
    for _ in 0..n_steps {
        let row: Vec<IntVar> = (0..cells).map(|_| IntVar::new(0..=max_v)).collect();
        board.push(row);
    }

    // The start and end boards are given.
    // The tiles are all different at every step.
    for c in 0..cells {
        post(s, iv(&board[0][c]), Comparator::Equal, start[c / k][c % k])?;
        post(s, iv(&board[n_steps - 1][c]), Comparator::Equal, end[c / k][c % k])?;
    }
    for t in 0..n_steps {
        all_different(s, &board[t])?;
    }

    // Unordered pairs of adjacent cells.
    let mut pairs: Vec<(usize, usize)> = Vec::new();
    for r in 0..k {
        for col in 0..k {
            let p = r * k + col;
            if col + 1 < k {
                pairs.push((p, p + 1));
            }
            if r + 1 < k {
                pairs.push((p, p + k));
            }
        }
    }

    // Each step moves the blank to a neighbouring cell: exactly one adjacent pair is
    // swapped, and the swapped pair holds the blank.
    for t in 0..n_steps - 1 {
        let zero: Vec<Lit> = (0..cells)
            .map(|c| reify_eq(s, iv(&board[t][c]), 0))
            .collect::<Res<Vec<Lit>>>()?;

        let mut sel: Vec<Lit> = Vec::with_capacity(pairs.len());
        let mut total = LinExp::default();
        for _ in &pairs {
            let l = s.new_lit();
            sel.push(l);
            total += LinExp::from(l);
        }
        post(s, total, Comparator::Equal, 1)?;

        // A cell is moved when a selected pair contains it.
        let mut moved: Vec<Lit> = Vec::with_capacity(cells);
        for c in 0..cells {
            let m = s.new_lit();
            let mut containing: Vec<Lit> = Vec::new();
            for (i, &(p, q)) in pairs.iter().enumerate() {
                if p == c || q == c {
                    containing.push(sel[i]);
                }
            }
            // m -> some containing pair is selected
            s.add_clause(std::iter::once(!m).chain(containing.iter().copied()))?;
            // a selected containing pair -> m
            for &l in &containing {
                s.add_clause([!l, m])?;
            }
            moved.push(m);
        }

        for (i, &(p, q)) in pairs.iter().enumerate() {
            let l = sel[i];
            // the swapped pair holds the blank
            s.add_clause([!l, zero[p], zero[q]])?;
            // the tiles on the two cells change places
            post_if(s, &[l], iv(&board[t + 1][p]) - iv(&board[t][q]), Comparator::Equal, 0)?;
            post_if(s, &[l], iv(&board[t + 1][q]) - iv(&board[t][p]), Comparator::Equal, 0)?;
        }

        // Cells that are not moved keep their tile.
        for c in 0..cells {
            post_if(
                s,
                &[!moved[c]],
                iv(&board[t + 1][c]) - iv(&board[t][c]),
                Comparator::Equal,
                0,
            )?;
        }
    }

    let steps: Vec<Vec<Vec<IntVar>>> = board
        .iter()
        .map(|b| (0..k).map(|r| b[r * k..(r + 1) * k].to_vec()).collect())
        .collect();
    let mut out = Out::new();
    out.put("steps", &steps);
    Ok(out)
}
