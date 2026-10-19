// All-interval series of size n (CSPLib 007): find a permutation x of 0..n-1 whose
// neighbour intervals |x[i+1] - x[i]| form a permutation of 1..n-1.

// Size n is read from the instance. The pitch-classes are 0..n-1 and the intervals are 1..n-1.
fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.size("n");

    // the series: s_1..s_n are pitch-classes, each in 0..n-1
    let x: Vec<IntVar> = (0..n).map(|_| IntVar::new(0..=(n as i64 - 1))).collect();
    // the intervals: v_1..v_{n-1} are the distances between neighbouring pitch-classes, each in 1..n-1
    let diffs: Vec<IntVar> = (0..n - 1).map(|_| IntVar::new(1..=(n as i64 - 1))).collect();

    // s is a permutation of Z_n: every pitch-class occurs exactly once
    all_different(s, &x)?;

    // the interval vector is a permutation of 1..n-1: every interval occurs exactly once
    all_different(s, &diffs)?;

    // each interval is the absolute difference of a pair of neighbouring pitch-classes
    // (the difference is defined as a fresh variable, then its absolute value is linked to the interval)
    for i in 0..n - 1 {
        let d = define(s, iv(&x[i + 1]) - iv(&x[i]))?;
        abs_eq(s, &d, &diffs[i])?;
    }

    let mut out = Out::new();
    out.put("x", &x).put("diffs", &diffs);
    Ok(out)
}
