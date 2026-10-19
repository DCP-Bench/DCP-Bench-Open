// Joe's account number: a permutation x of the digits 0..n-1 (n taken from the
// instance). Each set is a permutation of the same digits, and in each set exactly
// num_correct_digits positions hold the same digit as x in that position.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let sets = inst.matrix("sets");
    let n = sets[0].len();
    let k = inst.int("num_correct_digits");

    // The account number has all the digits from 0 to n-1 in some order.
    let x = m.new_int_decisions(n, 0..=(n as i64 - 1));
    m.unique(x.clone()).post()?;

    // In each set just a specific number of the digits were in their correct position.
    for s in &sets {
        let same: Vec<View<bool>> = (0..n).map(|j| x[j].eq(s[j])).collect();
        m.linear(same.iter().copied().sum::<IntLinearExp>()).eq(k).post()?;
    }

    let mut out = Out::new();
    out.put("x", x);
    Ok(out)
}
