// Equal-sized groups: a sorted list of n elements is divided into k groups by k-1 break points.
// A break point p (1-based) ends a group after element p. Items with the same value must stay
// in the same group, so a break point may only sit between two different values.
// Minimise the total error, the sum over the k groups of |group size - round(n/k)|.
fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let a = inst.ints("a");
    let n = a.len() as i64;
    let k = inst.int("k") as usize;

    // round(n / k), rounding half up, in integers.
    let target = (2 * n + k as i64) / (2 * k as i64);

    // Divide them into K groups by choosing K-1 split points between them.
    // Break points are 1-based positions p in 1..=n-1 with a[p-1] != a[p] (0-based a).
    // There may be elements with the same value, and it is necessary to have items with
    // the same value in the same group.
    let valid: Vec<Vec<i64>> = (1..n)
        .filter(|&p| a[(p - 1) as usize] != a[p as usize])
        .map(|p| vec![p])
        .collect();
    let mut ps: Vec<View<i64>> = Vec::new();
    for _ in 1..k {
        let p = m.new_int_decision(1..=n - 1);
        m.table(vec![p]).values(valid.clone()).post()?;
        ps.push(p);
    }
    // The split points are in increasing order.
    for j in 1..ps.len() {
        m.linear(ps[j - 1] - ps[j]).le(-1).post()?;
    }

    // Find K groups as close in size to round(N/K) as possible.
    // Each group size is target + d, where d is the deviation of that group.
    let mut devs: Vec<View<i64>> = Vec::new();
    for j in 0..k {
        let d = m.new_int_decision(-n..=n);
        if j == 0 {
            m.linear(ps[0] - d).eq(target).post()?;
        } else if j == k - 1 {
            m.linear(ps[k - 2] + d).eq(n - target).post()?;
        } else {
            m.linear(ps[j] - ps[j - 1] - d).eq(target).post()?;
        }
        devs.push(d);
    }

    // Print the 1-based indexes of the break points such that the total error is minimized,
    // where the total error is the sum of abs(size - round(N/K)) over the groups.
    let abss: Vec<View<i64>> = devs.iter().map(|&d| m.abs(d).define()).collect();
    let total = m.new_int_decision(0..=(k as i64) * n);
    m.linear(abss.iter().copied().sum::<IntLinearExp>()).eq(total).post()?;

    let mut out = Out::new();
    out.put("x", ps);
    out.minimise(total);
    Ok(out)
}
