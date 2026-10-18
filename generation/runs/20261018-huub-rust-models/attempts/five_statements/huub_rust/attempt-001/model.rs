// Five statements: determine which of five statements is true.
// Statement k (k = 1..5) says: "Exactly k of these statements are false."
// Output statements[k-1] is 1 if statement k is true, 0 otherwise.

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    let s: Vec<_> = (0..5).map(|_| m.new_bool_decision()).collect();

    // Exactly k of these statements are false, i.e. exactly 5 - k are true.
    // Statement k is true if and only if that holds.
    for k in 1..=5i64 {
        m.linear(s.iter().copied().sum::<IntLinearExp>())
            .eq(5 - k)
            .reified_by(s[(k - 1) as usize])
            .post()?;
    }

    let mut out = Out::new();
    out.put("statements", s);
    Ok(out)
}
