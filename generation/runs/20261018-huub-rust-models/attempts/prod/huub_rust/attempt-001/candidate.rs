// Problem prod: choose production quantities X[j] for each product j in P,
// with 0 <= X[j] <= u[j], to maximise the total profit sum c[j] * X[j],
// subject to sum (1/a[j]) * X[j] <= b.
// The fractions 1/a[j] are scaled by l = lcm(a) so every coefficient is an integer.

fn gcd(a: i64, b: i64) -> i64 {
    if b == 0 { a.abs() } else { gcd(b, a % b) }
}

fn lcm(a: i64, b: i64) -> i64 {
    a / gcd(a, b) * b
}

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let a = inst.ints("a");
    let c = inst.ints("c");
    let u = inst.ints("u");
    let b = inst.int("b");
    let n = a.len();

    // Variables X[j] with domain 0..=u[j], taken from the instance.
    // The description gives 0 <= X[j] <= u[j] for each j.
    let xs: Vec<View<i64>> = (0..n).map(|j| m.new_int_decision(0..=u[j])).collect();

    // The sum of (1/a[j]) * X[j] for all j should be less than or equal to b.
    // Multiplying by l = lcm(a) gives sum (l / a[j]) * X[j] <= b * l.
    let l = a.iter().fold(1i64, |acc, &aj| lcm(acc, aj));
    let capacity = xs
        .iter()
        .zip(a.iter())
        .map(|(x, &aj)| *x * (l / aj))
        .sum::<IntLinearExp>();
    m.linear(capacity).le(b * l).post()?;

    // The total profit is the sum of c[j] * X[j] for all j in P.
    // Its bounds follow from the domains of X[j].
    let lo: i64 = (0..n).map(|j| (c[j] * u[j]).min(0)).sum();
    let hi: i64 = (0..n).map(|j| (c[j] * u[j]).max(0)).sum();
    let total_profit = m.new_int_decision(lo..=hi);
    let profit = xs
        .iter()
        .zip(c.iter())
        .map(|(x, &cj)| *x * cj)
        .sum::<IntLinearExp>();
    m.linear(profit).eq(total_profit).post()?;

    let mut out = Out::new();
    out.put("x", xs).put("total_profit", total_profit);
    out.maximise(total_profit);
    Ok(out)
}
