// csplib 067: quasigroup completion. An order N quasigroup is an N x N Latin square:
// an N x N multiplication table in which each element from 1 to N occurs exactly once
// in every row and every column. Complete a partially filled quasigroup (puzzle).

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("N");
    let nn = inst.int("N");
    let start = inst.matrix("start");

    // The completed quasigroup: one integer cell per position, with values 1..N.
    let mut grid: Vec<Vec<View<i64>>> = Vec::with_capacity(n);
    for _ in 0..n {
        let mut row = Vec::with_capacity(n);
        for _ in 0..n {
            row.push(m.new_int_decision(1..=nn));
        }
        grid.push(row);
    }

    // Given cells keep their values; 0 marks an empty cell.
    for i in 0..n {
        for j in 0..n {
            let v = start[i][j];
            if v != 0 {
                m.linear(grid[i][j]).eq(v).post()?;
            }
        }
    }

    // Each element from 1 to N occurs exactly once in every row.
    for i in 0..n {
        m.unique(grid[i].clone()).post()?;
    }

    // Each element from 1 to N occurs exactly once in every column.
    for j in 0..n {
        let col: Vec<View<i64>> = (0..n).map(|i| grid[i][j]).collect();
        m.unique(col).post()?;
    }

    let mut out = Out::new();
    out.put("puzzle", grid);
    Ok(out)
}
