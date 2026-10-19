// Guards and apples: a boy has to pass num_gates gates to reach a girl. At each gate
// he bribes the guard with half of his apples, plus one. He cannot give a fraction of
// an apple, so the apples he has before a gate are even. After the last gate he has
// one apple left, which he gives to the girl, so he has none left.
// Output apples: the number of apples before each gate, then after the last gate.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("num_gates");
    // Generous upper bound on the apples at any point, from the number of gates.
    let max = 1i64 << (n + 2);

    // Apples before gate 0, ..., before gate n-1, and after the last gate.
    let apples = m.new_int_decisions(n + 1, 0..=max);

    for i in 0..n {
        // The guard gets half of his apples plus one, as a whole number of apples:
        // apples[i] = 2 * h, where h is half of his apples.
        let h = m.new_int_decision(0..=max);
        // apples[i] = 2 * h, posted as two inequalities.
        m.linear(apples[i] - h * 2).le(0).post()?;
        m.linear(apples[i] - h * 2).ge(0).post()?;

        // He gives h + 1 apples, so he keeps 2h - (h + 1) = h - 1 apples.
        // apples[i + 1] = h - 1, which means h - apples[i + 1] = 1.
        m.linear(h - apples[i + 1]).eq(1).post()?;
    }

    // After the last gate he has one apple, which he gives to the girl.
    m.linear(apples[n]).eq(1).post()?;

    let mut out = Out::new();
    out.put("apples", apples);
    Ok(out)
}
