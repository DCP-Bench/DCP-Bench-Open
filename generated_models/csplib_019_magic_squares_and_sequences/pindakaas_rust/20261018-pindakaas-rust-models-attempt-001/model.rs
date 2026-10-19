// csplib_019 magic sequence: find a sequence x_0, ..., x_{n-1} of integers between
// 0 and n-1 such that, for all i in 0 to n-1, the number i occurs exactly x_i times
// in the sequence. Print the magic sequence (x).

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.size("n");
    let hi = n as i64 - 1;

    // sequence of integers x_0, ..., x_{n-1} between 0 and n-1
    let x: Vec<IntVar> = (0..n).map(|_| IntVar::new(0..=hi)).collect();

    // for all i in 0 to n-1, the number i occurs exactly x_i times in the sequence
    for i in 0..n {
        count_eq(s, &x, i as i64, &x[i])?;
    }

    let mut out = Out::new();
    out.put("x", &x);
    Ok(out)
}
