// All-interval series of size n (CSPLib 007): find a sequence x of the pitch-classes 0..n-1,
// each occurring exactly once, such that the absolute intervals between neighbouring
// pitch-classes are exactly the values 1..n-1, each occurring once.
// n is read from the instance.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("n");
    let hi = n as i64 - 1;

    // the series x is a permutation of the pitch-classes 0..n-1 (each pitch-class occurs exactly once)
    let x = m.new_int_decisions(n, 0..=hi);
    m.unique(x.clone()).post()?;

    // the interval between neighbours x[i] and x[i+1] is |x[i+1] - x[i]|
    let mut diffs = Vec::new();
    for i in 0..n - 1 {
        let signed = m.new_int_decision(-hi..=hi);
        m.linear(x[i + 1] - x[i]).eq(signed).post()?;
        let d = m.abs(signed).define();
        // an interval is at least a minor second (1 semitone)
        m.linear(d).ge(1).post()?;
        diffs.push(d);
    }

    // the intervals cover the full set 1..n-1, each interval occurring exactly once
    m.unique(diffs.clone()).post()?;

    let mut out = Out::new();
    out.put("x", x).put("diffs", diffs);
    Ok(out)
}
