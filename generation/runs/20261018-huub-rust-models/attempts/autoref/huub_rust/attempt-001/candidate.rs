// Autoreferential series: find a series S = (s0, ..., sn, sn+1) of n+2 entries
// such that s_i is the number of occurrences of i in S, for each i from 0 to n,
// and the last entry sn+1 equals m. Output the series S.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("n");
    let target = inst.int("m");
    let len = n + 2;

    // The series S holds indices 0..=n only.
    // s_0 .. s_n: each entry is an index in 0..=n.
    let mut s: Vec<View<i64>> = Vec::with_capacity(len);
    for _ in 0..=n {
        s.push(m.new_int_decision(0..=n as i64));
    }
    // s_{n+1} = m, which must itself be an index in 0..=n.
    let last = m.new_int_decision(0..=n as i64);
    m.linear(last).eq(target).post()?;
    s.push(last);

    // The number of occurrences of i in S is s_i, for each i from 0 to n.
    for i in 0..=n {
        m.linear(count_eq(&s, i as i64)).eq(s[i]).post()?;
    }

    let mut out = Out::new();
    out.put("s", s);
    Ok(out)
}
