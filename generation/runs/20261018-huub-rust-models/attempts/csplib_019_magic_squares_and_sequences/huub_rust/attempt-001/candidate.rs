// Magic sequence (csplib 019): a sequence x_0..x_{n-1} of integers between 0 and n-1
// such that for all i in 0 to n-1, the number i occurs exactly x_i times in the sequence.
// The size n is read from the instance.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("n");

    // A magic sequence of length n is a sequence of integers between 0 and n-1.
    let x = m.new_int_decisions(n, 0..=(n as i64 - 1));

    // For all i in 0 to n-1, the number i occurs exactly x_i times in the sequence.
    for i in 0..n {
        m.linear(count_eq(&x, i as i64)).eq(x[i]).post()?;
    }

    let mut out = Out::new();
    out.put("x", x);
    Ok(out)
}
