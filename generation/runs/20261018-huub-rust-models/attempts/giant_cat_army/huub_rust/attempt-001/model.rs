// Giant cat army: a list of 24 integers, starting from [0] and ending with 14.
// Each step adds 5, adds 7, or takes the square root (the result must be an integer).
// All elements are distinct, all are <= 60, and 2, 10 and 14 appear in that order.

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    let n: usize = 24;
    let x = m.new_int_decisions(n, 0..=60);

    // The list starts with [0] and ends with 14.
    m.linear(x[0]).eq(0).post()?;
    m.linear(x[n - 1]).eq(14).post()?;

    // All elements are distinct.
    m.unique(x.clone()).post()?;

    // Each step is one of: adding 5, adding 7, or taking the square root.
    for i in 0..n - 1 {
        let add5 = m.new_bool_decision();
        let add7 = m.new_bool_decision();
        let root = m.new_bool_decision();
        m.linear(vec![add5, add7, root].into_iter().sum::<IntLinearExp>())
            .eq(1)
            .post()?;

        // Adding 5: the next element is the current one plus 5.
        m.linear(x[i + 1] - x[i]).ge(5).implied_by(add5).post()?;
        m.linear(x[i + 1] - x[i]).le(5).implied_by(add5).post()?;

        // Adding 7: the next element is the current one plus 7.
        m.linear(x[i + 1] - x[i]).ge(7).implied_by(add7).post()?;
        m.linear(x[i + 1] - x[i]).le(7).implied_by(add7).post()?;

        // Taking the square root: the next element s satisfies s * s = the current element.
        // s and sq are auxiliary; sq = s * s always holds, and it binds x only when root is true.
        let s = m.new_int_decision(0..=7);
        let sq = m.new_int_decision(0..=49);
        m.mul(s, s).result(sq).post()?;
        m.linear(x[i + 1] - s).ge(0).implied_by(root).post()?;
        m.linear(x[i + 1] - s).le(0).implied_by(root).post()?;
        m.linear(x[i] - sq).ge(0).implied_by(root).post()?;
        m.linear(x[i] - sq).le(0).implied_by(root).post()?;
    }

    // 2, 10 and 14 appear in that order: some 10 occurs, and every 10 is preceded by a 2.
    let mut is2 = Vec::with_capacity(n);
    let mut is10 = Vec::with_capacity(n);
    for i in 0..n {
        is2.push(m.linear(x[i]).eq(2).reify());
        is10.push(m.linear(x[i]).eq(10).reify());
    }
    m.linear(is10.iter().copied().sum::<IntLinearExp>())
        .ge(1)
        .post()?;
    for j in 1..n - 1 {
        m.linear(is2[..j].iter().copied().sum::<IntLinearExp>())
            .ge(1)
            .implied_by(is10[j])
            .post()?;
    }

    let mut out = Out::new();
    out.put("x", x);
    Ok(out)
}
