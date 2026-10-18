// csplib_049_number_partitioning: partition the numbers 1..N into two sets A and B
// with equal cardinality, equal sums and equal sums of squares. Print A and B.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.int("n");
    let half = inst.size("n") / 2;
    let mut out = Out::new();

    // A and B have the same cardinality. An odd N cannot be split that way.
    if n % 2 == 1 {
        let never = m.new_int_decision(0..=0);
        m.linear(never).eq(1).post()?;
    }

    // Every number of 1..N is used exactly once across A and B.
    let vals = m.new_int_decisions(2 * half, 1..=n);
    m.unique(vals.clone()).post()?;
    let a: Vec<View<i64>> = vals[..half].to_vec();
    let b: Vec<View<i64>> = vals[half..].to_vec();

    // Sum of numbers in A = sum of numbers in B.
    let total = m.new_int_decision(1..=n * (n + 1) / 2);
    m.linear(a.iter().copied().sum::<IntLinearExp>()).eq(total).post()?;
    m.linear(b.iter().copied().sum::<IntLinearExp>()).eq(total).post()?;

    // Sum of squares of numbers in A = sum of squares of numbers in B.
    let sq_a: Vec<View<i64>> = a.iter().map(|&v| m.mul(v, v).define()).collect();
    let sq_b: Vec<View<i64>> = b.iter().map(|&v| m.mul(v, v).define()).collect();
    let sq_total = m.new_int_decision(1..=n * (n + 1) * (2 * n + 1) / 6);
    m.linear(sq_a.iter().copied().sum::<IntLinearExp>()).eq(sq_total).post()?;
    m.linear(sq_b.iter().copied().sum::<IntLinearExp>()).eq(sq_total).post()?;

    out.put("A", a).put("B", b);
    Ok(out)
}
