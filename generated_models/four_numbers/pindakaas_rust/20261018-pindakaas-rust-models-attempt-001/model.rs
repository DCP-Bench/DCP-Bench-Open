// Four numbers: given up to four distinct integers between 1 and 10, find three integers x[0..3]
// between 1 and 10 such that every given number can be written as the sum of a subset of x.

// Find three integers x between 1 and 10 (inclusive).
// Every given number is the sum of some non-empty subset of x.
fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let numbers = inst.ints("numbers");
    let x: Vec<IntVar> = (0..3).map(|_| IntVar::new(1..=10)).collect();
    // For each given number, one of the seven non-empty subsets of x sums to it.
    for &n in &numbers {
        let mut options: Vec<Lit> = Vec::new();
        for mask in 1..8usize {
            let mut e = LinExp::default();
            for i in 0..3 {
                if mask & (1 << i) != 0 {
                    e += iv(&x[i]);
                }
            }
            options.push(reify_eq(s, e, n)?);
        }
        s.add_clause(options)?;
    }
    let mut out = Out::new();
    out.put("x", &x);
    Ok(out)
}
