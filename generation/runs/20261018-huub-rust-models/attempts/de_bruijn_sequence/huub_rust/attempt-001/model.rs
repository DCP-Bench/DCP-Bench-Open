// de Bruijn sequence of order n on an alphabet of size k (the instance's base).
// A cyclic sequence of length k^n in which every possible length-n string over the
// alphabet occurs exactly once as a substring. The declared output is the sequence.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let k = inst.int("base");
    let n = inst.size("n");
    let len = k.pow(n as u32) as usize;

    // The sequence: len digits in 0..k-1.
    let xs = m.new_int_decisions(len, 0..=k - 1);

    // A cyclic sequence of length k^n in which every possible length-n string over the
    // alphabet occurs exactly once as a substring.
    // Each length-n window (starting at position i, wrapping around) is read as a
    // base-k number w_i; the k^n windows must all differ, so they take every value 0..k^n-1.
    let mut ws = Vec::with_capacity(len);
    for i in 0..len {
        let w = m.new_int_decision(0..=(len as i64) - 1);
        let value: IntLinearExp = (0..n)
            .map(|j| IntLinearExp::from(xs[(i + j) % len] * k.pow((n - 1 - j) as u32)))
            .sum();
        m.linear(value).eq(w).post()?;
        ws.push(w);
    }
    m.unique(ws).post()?;

    let mut out = Out::new();
    out.put("de_bruijn", xs);
    Ok(out)
}
