// Problem autoref: given n > 0 and m >= 0, find a non-empty finite series
// S = (s0, s1, ..., sn, sn+1) such that (1) there are si occurrences of i in S
// for each integer i from 0 to n, and (2) sn+1 = m. Output the series S as s.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.size("n");
    let m = inst.int("m");
    // Every entry of S is counted by one of the values 0..n, so every entry lies in 0..n.
    let top = n as i64;
    let xs: Vec<IntVar> = (0..=n + 1).map(|_| IntVar::new(0..=top)).collect();

    // There are si occurrences of i in S for each integer i from 0 to n.
    for i in 0..=n {
        count_eq(s, &xs, i as i64, &xs[i])?;
    }

    // The last entry of the series is sn+1 = m.
    post(s, iv(&xs[n + 1]), Comparator::Equal, m)?;

    let mut out = Out::new();
    out.put("s", &xs);
    Ok(out)
}
