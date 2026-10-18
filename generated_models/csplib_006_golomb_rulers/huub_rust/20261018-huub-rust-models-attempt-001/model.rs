// Golomb ruler (csplib 006): m marks 0 = a_1 < a_2 < ... < a_m such that the
// m(m-1)/2 differences a_j - a_i (i < j) are pairwise distinct. Minimise the
// length a_m. Outputs: marks (a_1..a_m) and length (a_m).

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("size");
    // The optimal length is well below n*n, so n*n bounds every mark.
    let ub = (n * n) as i64;

    // the first mark is 0
    let mut a = Vec::with_capacity(n);
    a.push(m.new_int_decision(0..=0));
    for _ in 1..n {
        a.push(m.new_int_decision(0..=ub));
    }

    // the marks are strictly increasing: a_1 < a_2 < ... < a_m
    for i in 0..n - 1 {
        m.linear(a[i]).lt(a[i + 1]).post()?;
    }

    // the m(m-1)/2 differences a_j - a_i, for i < j, are pairwise distinct
    let mut diffs = Vec::with_capacity(n * (n - 1) / 2);
    for i in 0..n {
        for j in (i + 1)..n {
            let d = m.new_int_decision(1..=ub);
            m.linear(a[j] - a[i]).eq(d).post()?;
            diffs.push(d);
        }
    }
    m.unique(diffs).post()?;

    // the length of the ruler is the last mark, to be minimised
    let length = a[n - 1];
    let mut out = Out::new();
    out.put("length", length).put("marks", a.clone());
    out.minimise(length);
    Ok(out)
}
