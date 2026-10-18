// Problem "among": requires exactly m values in x to take one of the values in v.
// All other values may be anything larger than or equal to 0 and less than or equal to 7.
// Output: the array x.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("n");
    let count = inst.int("m");
    let v = inst.ints("v");

    // Every entry of x is between 0 and 7.
    let x = m.new_int_decisions(n, 0..=7);

    // Requires exactly m values in x to take one of the values in v.
    // Each entry gets a Boolean that holds iff the entry is a member of v.
    let set = Set::from_iter(v.iter().map(|&k| k..=k));
    let mut bs = Vec::with_capacity(n);
    for &xi in &x {
        let b = m.contains(set.clone()).member(xi).define();
        bs.push(b);
    }
    m.linear(bs.iter().copied().sum::<IntLinearExp>()).eq(count).post()?;

    let mut out = Out::new();
    out.put("x", x);
    Ok(out)
}
