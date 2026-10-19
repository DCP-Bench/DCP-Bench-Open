// Nonogram (csplib 012): shade squares of a rows x cols grid so that the blocks of
// consecutive shaded squares in each row and each column match that line's clue.
// A clue lists the block lengths in order; the data pads it with leading zeros, so
// only the nonzero entries are blocks. The output board holds 1 for a shaded square
// and 0 for an unshaded one.

// The block lengths of a padded clue, in order, with the zero padding dropped.
fn runs(clue: &[i64]) -> Vec<usize> {
    clue.iter().filter(|&&b| b > 0).map(|&b| b as usize).collect()
}

// A line of cells spells out the blocks `b`: one run of shaded cells per block, in
// order, with at least one unshaded cell between two consecutive blocks.
// It is encoded as a deterministic automaton over the cells. State (j, c): c shaded
// cells of block j have been read; (j, 0) waits before block j, and (j, b_j) has just
// finished block j. The state after the last cell must be accepting. A literal stands
// for each state that is reachable at a position and can still reach acceptance;
// exactly one of them is true per position, and each one forces its successor.
fn encode_line(s: &mut Cadical, cells: &[Lit], b: &[usize]) -> Res {
    let n = cells.len();
    let k = b.len();
    let mut base = vec![0usize; k + 1];
    let mut total = 0usize;
    for j in 0..k {
        base[j] = total;
        total += b[j] + 1;
    }
    base[k] = total;
    total += 1;
    let mut decode = vec![(k, 0usize); total];
    for j in 0..k {
        for c in 0..=b[j] {
            decode[base[j] + c] = (j, c);
        }
    }
    let step = |q: usize, v: bool| -> Option<usize> {
        let (j, c) = decode[q];
        if j == k {
            return if v { None } else { Some(q) };
        }
        if c == 0 {
            Some(if v { base[j] + 1 } else { q })
        } else if c < b[j] {
            if v { Some(q + 1) } else { None }
        } else if v {
            None
        } else {
            Some(base[j + 1])
        }
    };
    let mut accept = vec![base[k]];
    if k > 0 {
        accept.push(base[k - 1] + b[k - 1]);
    }

    // Forward reachability and backward co-reachability from the accepting states.
    let mut reach = vec![vec![false; total]; n + 1];
    reach[0][base[0]] = true;
    for i in 0..n {
        for q in 0..total {
            if !reach[i][q] {
                continue;
            }
            for v in [false, true] {
                if let Some(t) = step(q, v) {
                    reach[i + 1][t] = true;
                }
            }
        }
    }
    let mut coreach = vec![vec![false; total]; n + 1];
    for &q in &accept {
        coreach[n][q] = true;
    }
    for i in (0..n).rev() {
        for q in 0..total {
            for v in [false, true] {
                if let Some(t) = step(q, v) {
                    if coreach[i + 1][t] {
                        coreach[i][q] = true;
                    }
                }
            }
        }
    }

    // One literal per feasible state, exactly one true per position.
    let mut lit: Vec<Vec<Option<Lit>>> = vec![vec![None; total]; n + 1];
    for i in 0..=n {
        let mut states = Vec::new();
        for q in 0..total {
            if reach[i][q] && coreach[i][q] {
                let l = s.new_lit();
                lit[i][q] = Some(l);
                states.push(l);
            }
        }
        if states.is_empty() {
            s.add_clause(Vec::<Lit>::new())?;
        } else if states.len() == 1 {
            s.add_clause([states[0]])?;
        } else {
            let mut e = LinExp::default();
            for &l in &states {
                e += bx(BoolVal::Lit(l));
            }
            post(s, e, Comparator::Equal, 1)?;
        }
    }

    // Transitions: a state with a literal, read one cell with value v, moves to its
    // successor. A cell value with no feasible successor is forbidden in that state.
    for i in 0..n {
        for q in 0..total {
            if let Some(ql) = lit[i][q] {
                for v in [false, true] {
                    let differs = if v { !cells[i] } else { cells[i] };
                    match step(q, v).and_then(|t| lit[i + 1][t]) {
                        Some(tl) => s.add_clause([!ql, differs, tl])?,
                        None => s.add_clause([!ql, differs])?,
                    }
                }
            }
        }
    }

    // The first position is in the start state.
    if let Some(start) = lit[0][base[0]] {
        s.add_clause([start])?;
    }
    Ok(())
}

// Shade squares so that the blocks of consecutive shaded squares in each row and in
// each column match the clue given for that row or column.
fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let rows = inst.size("rows");
    let cols = inst.size("cols");
    let row_rules = inst.matrix("row_rules");
    let col_rules = inst.matrix("col_rules");

    // One 0/1 integer per square, 1 for shaded.
    let board: Vec<Vec<IntVar>> = (0..rows)
        .map(|_| (0..cols).map(|_| IntVar::new(0..=1)).collect())
        .collect();
    let mut shaded: Vec<Vec<Lit>> = Vec::new();
    for row in &board {
        let mut line = Vec::new();
        for x in row {
            let on = x.equals(s, 1)?;
            line.push(lit_of(s, on)?);
        }
        shaded.push(line);
    }

    // Each row's blocks of consecutive shaded squares must match the constraint given for that row.
    for (r, line) in shaded.iter().enumerate() {
        encode_line(s, line, &runs(&row_rules[r]))?;
    }

    // Each column's blocks of consecutive shaded squares must match the constraint given for that column.
    for c in 0..cols {
        let column: Vec<Lit> = (0..rows).map(|r| shaded[r][c]).collect();
        encode_line(s, &column, &runs(&col_rules[c]))?;
    }

    let mut out = Out::new();
    out.put("board", &board);
    Ok(out)
}
