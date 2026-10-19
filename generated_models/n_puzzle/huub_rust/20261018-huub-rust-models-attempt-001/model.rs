// N-puzzle: trace N_STEPS grid states from puzzle_start to puzzle_end.
// Each state is a square grid of tiles numbered 0..n*n-1, where 0 is the empty cell.
// Every state is a permutation of the tiles; the grid size comes from the instance.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let steps = inst.size("N_STEPS");
    let start = inst.matrix("puzzle_start");
    let end = inst.matrix("puzzle_end");
    let n = start.len();
    let cells = n * n;
    let max_val = (cells - 1) as i64;

    // Cell k of step t holds a tile value; blank[t][k] says the empty cell is k at step t.
    let mut g: Vec<Vec<View<i64>>> = Vec::new();
    let mut blank: Vec<Vec<View<bool>>> = Vec::new();
    let mut bp: Vec<View<i64>> = Vec::new();
    for _ in 0..steps {
        g.push(m.new_int_decisions(cells, 0..=max_val));
        bp.push(m.new_int_decision(0..=max_val));
    }
    for t in 0..steps {
        let mut row = Vec::new();
        for k in 0..cells {
            row.push(m.linear(bp[t]).eq(k as i64).reify());
        }
        blank.push(row);
    }

    // Each state uses every tile value exactly once.
    for t in 0..steps {
        m.unique(g[t].clone()).post()?;
    }

    // The empty cell is the cell whose value is 0 in that state.
    for t in 0..steps {
        for k in 0..cells {
            m.linear(g[t][k]).eq(0).reified_by(blank[t][k]).post()?;
        }
    }

    // The first state is puzzle_start and the last state is puzzle_end.
    for i in 0..n {
        for j in 0..n {
            m.linear(g[0][i * n + j]).eq(start[i][j]).post()?;
            m.linear(g[steps - 1][i * n + j]).eq(end[i][j]).post()?;
        }
    }

    // The empty cell moves to an adjacent cell at every step, so the state changes at every step.
    let mut adjacent: Vec<Vec<i64>> = Vec::new();
    for p in 0..n {
        for q in 0..n {
            for (dr, dc) in [(0i64, 1i64), (1, 0), (0, -1), (-1, 0)] {
                let r2 = p as i64 + dr;
                let c2 = q as i64 + dc;
                if r2 >= 0 && r2 < n as i64 && c2 >= 0 && c2 < n as i64 {
                    let a = (p * n + q) as i64;
                    let b = (r2 as usize * n + c2 as usize) as i64;
                    adjacent.push(vec![a, b]);
                }
            }
        }
    }
    for t in 0..steps - 1 {
        m.table(vec![bp[t], bp[t + 1]]).values(adjacent.clone()).post()?;
    }

    // Between two steps, the tile that moves is the one in the cell the empty cell moves to.
    // Every other cell keeps its tile. The empty cell takes the moved tile, and the cell it leaves is empty.
    for t in 0..steps - 1 {
        let tv = m.new_int_decision(0..=max_val);
        m.element(g[t].clone()).index(bp[t + 1]).result(tv).post()?;
        for k in 0..cells {
            let a = blank[t][k];
            let b = blank[t + 1][k];
            let stay = m
                .linear([a, b].into_iter().sum::<IntLinearExp>())
                .eq(0)
                .reify();
            m.linear(g[t + 1][k] - g[t][k]).eq(0).implied_by(stay).post()?;
            m.linear(g[t + 1][k]).eq(tv).implied_by(a).post()?;
            m.linear(g[t + 1][k]).eq(0).implied_by(b).post()?;
        }
    }

    // Output the grid of every step, as steps[t][row][col].
    let mut grids: Vec<Vec<Vec<View<i64>>>> = Vec::new();
    for t in 0..steps {
        let grid: Vec<Vec<View<i64>>> = (0..n).map(|i| g[t][i * n..(i + 1) * n].to_vec()).collect();
        grids.push(grid);
    }
    let mut out = Out::new();
    out.put("steps", grids);
    Ok(out)
}
