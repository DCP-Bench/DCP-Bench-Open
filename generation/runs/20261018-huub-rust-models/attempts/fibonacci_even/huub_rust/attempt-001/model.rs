// Problem fibonacci_even: sum the even-valued terms of the Fibonacci sequence
// that do not exceed four million. The sequence starts with 1 and 2, and each
// new term is the sum of the previous two. The output res is that sum.
// The instance carries no data; the bounds below are fixed mathematical constants.

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    // Number of terms modelled. Terms from index 33 on exceed four million,
    // so 40 terms cover every term the sum can include.
    const N: usize = 40;
    const LIMIT: i64 = 4_000_000;

    // Each new term is the sum of the previous two terms, starting from 1 and 2.
    let f = m.new_int_decisions(N, 0..=1_000_000_000);
    m.linear(f[0]).eq(1).post()?;
    m.linear(f[1]).eq(2).post()?;
    for i in 2..N {
        m.linear(f[i] - f[i - 1] - f[i - 2]).eq(0).post()?;
    }

    // A term counts when it does not exceed four million and is even.
    // Each term is either selected (its value) or contributes zero.
    let mut selected = Vec::with_capacity(N);
    for i in 0..N {
        // Indicator: the term does not exceed four million.
        let small = m.linear(f[i]).le(LIMIT).reify();

        // Indicator: the term is even, written as term = 2 * half.
        let half = m.new_int_decision(0..=500_000_000);
        let even = m.linear(f[i] - half * 2).eq(0).reify();

        // Both conditions hold, or not.
        let both = m
            .linear([small, even].into_iter().sum::<IntLinearExp>())
            .eq(2)
            .reify();
        let not_both = m
            .linear([small, even].into_iter().sum::<IntLinearExp>())
            .le(1)
            .reify();

        // The selected value equals the term when both hold, and zero otherwise.
        let g = m.new_int_decision(0..=LIMIT);
        m.linear(g - f[i]).eq(0).reified_by(both).post()?;
        m.linear(g).eq(0).reified_by(not_both).post()?;
        selected.push(g);
    }

    // res is the sum of the selected values.
    let res = m.new_int_decision(0..=100_000_000);
    m.linear(selected.iter().copied().sum::<IntLinearExp>())
        .eq(res)
        .post()?;

    let mut out = Out::new();
    out.put("res", res);
    Ok(out)
}
