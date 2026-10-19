// Session 1 guards and apples: a boy passes num_gates gates to give an apple to a girl.
// At each gate the guard takes half of his apples plus one, as an integer number of apples.
// After the last gate he has one apple left, which he gives to the girl, and then none.
// apples[i] is the count before gate i, apples[num_gates] the count after the last gate.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.size("num_gates");
    let hi = 3i64 << n;
    let apples: Vec<IntVar> = (0..=n).map(|_| IntVar::new(0..=hi)).collect();

    // He bribes each guard with half of his apples, plus one, giving an integer number:
    // apples[i] is even and apples[i+1] = apples[i] / 2 - 1, i.e. apples[i] = 2 * apples[i+1] + 2.
    for i in 0..n {
        post(s, iv(&apples[i]) - scaled(&apples[i + 1], 2), Comparator::Equal, 2)?;
    }

    // After he's given the apple to the girl, he has no apples left: one apple remains after the last gate.
    post(s, iv(&apples[n]), Comparator::Equal, 1)?;

    let mut out = Out::new();
    out.put("apples", &apples);
    Ok(out)
}
