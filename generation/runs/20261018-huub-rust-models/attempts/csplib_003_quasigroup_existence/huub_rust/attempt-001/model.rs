// Quasigroup existence, QG3.m: an order m quasigroup is an m x m multiplication
// table with values 0..m-1 in which each element occurs once in every row and column.
// QG3.m problems additionally satisfy (a*b)*(b*a) = a for all a, b.
// The output "quasigroup" is the m x m table; m comes from the instance.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("m");
    let ni = n as i64;

    // The multiplication table: one value in 0..m-1 per cell.
    let mut q: Vec<Vec<View<i64>>> = Vec::new();
    for _ in 0..n {
        let mut row: Vec<View<i64>> = Vec::new();
        for _ in 0..n {
            row.push(m.new_int_decision(0..=ni - 1));
        }
        q.push(row);
    }

    // Each element occurs once in every row and column of the table.
    for i in 0..n {
        let row: Vec<View<i64>> = (0..n).map(|j| q[i][j].clone()).collect();
        m.unique(row).post()?;
    }
    for j in 0..n {
        let col: Vec<View<i64>> = (0..n).map(|i| q[i][j].clone()).collect();
        m.unique(col).post()?;
    }

    // Flattened table, so that a cell can be looked up by index c * m + d.
    let flat: Vec<View<i64>> = (0..n)
        .flat_map(|i| (0..n).map(move |j| (i, j)))
        .map(|(i, j)| q[i][j].clone())
        .collect();

    // (a*b)*(b*a) = a: with c = a*b and d = b*a, the cell q[c][d] must equal a.
    // The lookup index idx = c * m + d is posted as a linear equality.
    for a in 0..n {
        for b in 0..n {
            let c = q[a][b].clone();
            let d = q[b][a].clone();
            let idx = m.new_int_decision(0..=ni * ni - 1);
            m.linear(c * ni + d).eq(idx).post()?;
            let r = m.element(flat.clone()).index(idx).define();
            m.linear(r).eq(a as i64).post()?;
        }
    }

    let mut out = Out::new();
    out.put("quasigroup", q);
    Ok(out)
}
