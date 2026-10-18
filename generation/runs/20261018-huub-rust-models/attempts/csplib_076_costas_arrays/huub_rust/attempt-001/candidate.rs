// csplib_076 Costas arrays: n marks on an n x n grid, one mark per row and one
// per column, such that the n(n-1)/2 vectors between the marks are all different.
// Output costas: the 1-based column of the mark in each row.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("n");
    let ni = n as i64;

    // One mark per row and one per column: the X_1..X_n form a permutation of 1..n.
    let x = m.new_int_decisions(n, 1..=ni);
    m.unique(x.clone()).post()?;

    // Difference triangle: for each length l in 1..n-1, add n-l variables
    // X_{l1}..X_{ln-l}, where X_{li} = X_i - X_{i+l}.
    // Each line of this triangle must not contain any value twice.
    for l in 1..n {
        let mut line = Vec::with_capacity(n - l);
        for i in 0..n - l {
            let d = m.new_int_decision(-(ni - 1)..=(ni - 1));
            m.linear(x[i] - x[i + l]).eq(d).post()?;
            line.push(d);
        }
        m.unique(line).post()?;
    }

    let mut out = Out::new();
    out.put("costas", x);
    Ok(out)
}
