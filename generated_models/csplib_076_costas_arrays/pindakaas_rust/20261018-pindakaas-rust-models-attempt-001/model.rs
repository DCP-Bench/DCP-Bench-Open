// csplib 076, Costas arrays. A Costas array of order n is a pattern of n marks on an
// n x n grid, one mark per row and one per column, in which the n(n-1)/2 vectors between
// the marks are all different. The output costas lists n integers, 1-based.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.size("n");
    let ni = n as i64;

    // Variables X_1, ..., X_n take values 1..n.
    let x: Vec<IntVar> = (0..n).map(|_| IntVar::new(1..=ni)).collect();

    // The marks form a permutation: X_1, ..., X_n all different.
    all_different(s, &x)?;

    // Difference triangle: for each length l in 1..n-1, the n-l variables
    // X_{l,i} = X_i - X_{i+l} for i in 1..n-l.
    // Each line of this difference triangle must not contain any value twice.
    for l in 1..n {
        let mut line: Vec<IntVar> = Vec::with_capacity(n - l);
        for i in 0..(n - l) {
            let d = define(s, iv(&x[i]) + scaled(&x[i + l], -1))?;
            line.push(d);
        }
        all_different(s, &line)?;
    }

    let mut out = Out::new();
    out.put("costas", &x);
    Ok(out)
}
