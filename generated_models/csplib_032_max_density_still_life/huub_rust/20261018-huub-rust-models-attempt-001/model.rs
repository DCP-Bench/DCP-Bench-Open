// csplib_032 maximum density still life: an n x m active grid of cells, each live (1) or dead (0).
// Cells outside the grid are dead and are part of the board.

// A live cell must have exactly 2 or 3 live neighbours to remain alive.
// A dead cell, including any dead cell just outside the active grid, must not have exactly 3 live neighbours.
// The goal is to maximise the number of live cells in the active grid.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("n");
    let cols = inst.size("m");

    let mut grid: Vec<Vec<View<bool>>> = Vec::new();
    for _ in 0..n {
        let mut row: Vec<View<bool>> = Vec::new();
        for _ in 0..cols {
            row.push(m.new_bool_decision());
        }
        grid.push(row);
    }

    // Every cell of the board around the grid, including the ring of dead cells just outside it.
    for r in -1i64..=(n as i64) {
        for c in -1i64..=(cols as i64) {
            let mut nb: Vec<View<bool>> = Vec::new();
            for dr in -1i64..=1 {
                for dc in -1i64..=1 {
                    if dr == 0 && dc == 0 {
                        continue;
                    }
                    let rr = r + dr;
                    let cc = c + dc;
                    if rr >= 0 && rr < n as i64 && cc >= 0 && cc < cols as i64 {
                        nb.push(grid[rr as usize][cc as usize]);
                    }
                }
            }
            if nb.is_empty() {
                continue;
            }

            let inside = r >= 0 && r < n as i64 && c >= 0 && c < cols as i64;
            if inside {
                // Live cell: 2 or 3 live neighbours.
                let x = grid[r as usize][c as usize];
                let s_lo = nb.iter().copied().sum::<IntLinearExp>();
                m.linear(s_lo).ge(2).implied_by(x).post()?;
                let s_hi = nb.iter().copied().sum::<IntLinearExp>();
                m.linear(s_hi).le(3).implied_by(x).post()?;
                // Dead cell: not exactly 3 live neighbours.
                let s_ne = nb.iter().copied().sum::<IntLinearExp>();
                let ne3 = m.linear(s_ne).ne(3).reify();
                m.proposition(BoolFormula::Atom(x) | BoolFormula::Atom(ne3)).post()?;
            } else {
                // Dead cell outside the grid: not exactly 3 live neighbours.
                let s_out = nb.iter().copied().sum::<IntLinearExp>();
                m.linear(s_out).ne(3).post()?;
            }
        }
    }

    // Objective: number of live cells.
    let total = grid.iter().flatten().copied().sum::<IntLinearExp>();
    let obj = m.new_int_decision(0..=((n * cols) as i64));
    m.linear(total).eq(obj).post()?;

    let mut out = Out::new();
    out.put("grid", grid);
    out.maximise(obj);
    Ok(out)
}
