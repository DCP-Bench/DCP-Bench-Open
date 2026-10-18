// Devil's word: given an array of integers, insert '+' or '-' before each integer
// so that the signed sum is `total`. Output `result`: the signed integers, so
// result[i] is +arr[i] or -arr[i].

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let arr = inst.ints("arr");
    let total = inst.int("total");

    // Insert '+' or '-' before each integer in the array.
    // A 0/1 sign variable s picks '+' (0) or '-' (1), and r = arr[i] - 2 * arr[i] * s.
    let mut result: Vec<View<i64>> = Vec::with_capacity(arr.len());
    for &a in &arr {
        let s = m.new_int_decision(0..=1);
        let (lo, hi) = (a.min(-a), a.max(-a));
        let r = m.new_int_decision(lo..=hi);
        m.linear(r + s * (2 * a)).eq(a).post()?;
        result.push(r);
    }

    // Summing them up will result in the total.
    let sum: IntLinearExp = result.iter().map(|r| IntLinearExp::from(*r)).sum();
    m.linear(sum).eq(total).post()?;

    let mut out = Out::new();
    out.put("result", result);
    Ok(out)
}
