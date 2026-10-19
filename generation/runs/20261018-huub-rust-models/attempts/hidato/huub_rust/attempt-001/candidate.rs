// Hidato puzzle: fill an R x C grid with the numbers 1..R*C, all different,
// so that every number touches the next one horizontally, vertically or
// diagonally. The numbers given in the puzzle keep their cells.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let puzzle = inst.matrix("puzzle");
    let rows = puzzle.len();
    let cols = puzzle[0].len();
    let cells = rows * cols;
    let k = cells as i64;

    // The grid: one value per cell, all different, in 1..=K.
    // Every number 1..=K is used, since there are K cells.
    let flat = m.new_int_decisions(cells, 1..=k);
    m.unique(flat.clone()).post()?;

    // The numbers given in the puzzle keep their cells.
    for r in 0..rows {
        for c in 0..cols {
            let v = puzzle[r][c];
            if v != 0 {
                m.linear(flat[r * cols + c]).eq(v).post()?;
            }
        }
    }

    // at[v][c] holds exactly when cell c has the number v.
    let mut at: Vec<Vec<View<bool>>> = Vec::with_capacity(cells + 1);
    at.push(Vec::new());
    for v in 1..=k {
        let mut row: Vec<View<bool>> = Vec::with_capacity(cells);
        for c in 0..cells {
            let b = m.linear(flat[c]).eq(v).reify();
            row.push(b);
        }
        // Each number sits in exactly one cell.
        m.linear(row.iter().copied().sum::<IntLinearExp>())
            .eq(1)
            .post()?;
        at.push(row);
    }

    // Consecutive numbers touch: if v is in cell c, then v + 1 is in one of
    // the neighbours of c (8-neighbourhood). Since each number is in exactly
    // one cell, this forces the cells of 1, 2, ..., K to form a path.
    for v in 1..k {
        let vu = v as usize;
        for c in 0..cells {
            let r = (c / cols) as i64;
            let col = (c % cols) as i64;
            let mut nbr: Vec<View<bool>> = Vec::new();
            for dr in -1i64..=1 {
                for dc in -1i64..=1 {
                    if dr == 0 && dc == 0 {
                        continue;
                    }
                    let nr = r + dr;
                    let nc = col + dc;
                    if nr >= 0 && nr < rows as i64 && nc >= 0 && nc < cols as i64 {
                        nbr.push(at[vu + 1][(nr as usize) * cols + nc as usize]);
                    }
                }
            }
            m.linear(nbr.iter().copied().sum::<IntLinearExp>())
                .ge(1)
                .implied_by(at[vu][c])
                .post()?;
        }
    }

    let mut grid: Vec<Vec<View<i64>>> = Vec::with_capacity(rows);
    for r in 0..rows {
        grid.push(flat[r * cols..(r + 1) * cols].to_vec());
    }
    let mut out = Out::new();
    out.put("x", grid);
    Ok(out)
}
