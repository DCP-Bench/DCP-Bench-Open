// Find a 10 digit number that uses each of the digits 0 to 9 exactly once and
// where the number formed by the first n digits is divisible by n (n = 1..10).
// The output "number" is the full 10 digit number.

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    // The digits of the number, read left to right. Each of 0 to 9 is used exactly once.
    let d = m.new_int_decisions(10, 0..=9);
    m.unique(d.clone()).post()?;

    // A 10 digit number does not start with 0.
    m.linear(d[0].clone()).ge(1).post()?;

    // Prefix values: p[k] is the number formed by the first k+1 digits.
    // The prefix of length n = k+1 is divisible by n when p[k] == n * q for some integer q.
    // The prefix is built from the previous one: p[k] == 10 * p[k-1] + d[k].
    let mut p: Vec<View<i64>> = vec![d[0].clone()];
    for k in 1..10usize {
        let n = k as i64 + 1;
        let max = 10i64.pow(k as u32 + 1) - 1;
        let pk = m.new_int_decision(0..=max);
        m.linear(p[k - 1].clone() * 10 + d[k].clone() - pk.clone()).eq(0).post()?;

        // The prefix of length n is divisible by n.
        let q = m.new_int_decision(0..=max / n);
        eq2(m, pk.clone() - q.clone() * n, 0)?;
        p.push(pk);
    }

    let mut out = Out::new();
    out.put("number", p[9].clone());
    Ok(out)
}
