// Coins on an n by n grid: place coins so that every row and every column
// holds exactly c coins, at most one coin per cell, and minimise the sum of
// the quadratic horizontal distance from the main diagonal over all cells
// that contain a coin.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("n");
    let c = inst.int("c");

    // A cell holds a coin (1) or not (0). At most one coin per cell.
    let mut x: Vec<Vec<View<i64>>> = Vec::new();
    for _ in 0..n {
        let mut row: Vec<View<i64>> = Vec::new();
        for _ in 0..n {
            row.push(m.new_int_decision(0..=1));
        }
        x.push(row);
    }

    // In each row exactly c coins must be placed.
    for i in 0..n {
        let row_sum: IntLinearExp = x[i].iter().map(|v| IntLinearExp::from(*v)).sum();
        m.linear(row_sum).eq(c).post()?;
    }

    // In each column exactly c coins must be placed.
    for j in 0..n {
        let col_sum: IntLinearExp = (0..n).map(|i| IntLinearExp::from(x[i][j])).sum();
        m.linear(col_sum).eq(c).post()?;
    }

    // The sum of the quadratic horizontal distance from the main diagonal of
    // all cells containing a coin must be as small as possible.
    let mut terms: Vec<IntLinearExp> = Vec::new();
    let mut max_total: i64 = 0;
    for i in 0..n {
        for j in 0..n {
            let di = i as i64 - j as i64;
            let d = di * di;
            max_total += d;
            terms.push(IntLinearExp::from(x[i][j] * d));
        }
    }
    let obj_expr: IntLinearExp = terms.into_iter().sum();
    let z = m.new_int_decision(0..=max_total);
    m.linear(obj_expr).eq(z).post()?;

    let mut out = Out::new();
    out.put("x", x).put("z", z);
    out.minimise(z);
    Ok(out)
}
