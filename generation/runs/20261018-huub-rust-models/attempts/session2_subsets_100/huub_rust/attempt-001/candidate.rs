// Problem session2_subsets_100: given a set A of distinct integers, find two
// disjoint non-empty subsets S and T of A whose element sums are equal.
// S union T need not cover A. Output in_S and in_T as 0/1 lists over A.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let a = inst.ints("A");
    let n = a.len();

    let s: Vec<View<bool>> = (0..n).map(|_| m.new_bool_decision()).collect();
    let t: Vec<View<bool>> = (0..n).map(|_| m.new_bool_decision()).collect();

    // 0/1 integer views of the membership flags, for the sums.
    let xs: Vec<View<i64>> = (0..n).map(|_| m.new_int_decision(0..=1)).collect();
    let ys: Vec<View<i64>> = (0..n).map(|_| m.new_int_decision(0..=1)).collect();
    for i in 0..n {
        m.linear(xs[i]).eq(1).reified_by(s[i]).post()?;
        m.linear(ys[i]).eq(1).reified_by(t[i]).post()?;
    }

    // S and T are disjoint: no element is in both subsets.
    for i in 0..n {
        m.linear(xs[i] + ys[i]).le(1).post()?;
    }

    // S is non-empty.
    m.linear(xs.iter().copied().sum::<IntLinearExp>())
        .ge(1)
        .post()?;

    // T is non-empty.
    m.linear(ys.iter().copied().sum::<IntLinearExp>())
        .ge(1)
        .post()?;

    // The sum of the elements in S equals the sum of the elements in T.
    let mut diff = IntLinearExp::from(0i64);
    for i in 0..n {
        diff = diff + xs[i] * a[i] - ys[i] * a[i];
    }
    m.linear(diff).eq(0).post()?;

    let mut out = Out::new();
    out.put("in_S", s).put("in_T", t);
    Ok(out)
}
