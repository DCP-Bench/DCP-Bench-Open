// Fifty puzzle (side show): ten dummies with numbers on them. Knock over a
// subset of the dummies so that the sum of their numbers is exactly the target
// sum. Output dummies[i] is true when dummy i is knocked over.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let values = inst.ints("values");
    let target = inst.int("target_sum");
    let n = values.len();

    // A dummy is knocked over when its Boolean is true.
    let dummies: Vec<View<bool>> = (0..n).map(|_| m.new_bool_decision()).collect();

    // The numbers on the knocked-over dummies add up to exactly the target sum.
    // Each dummy contributes its number when knocked over, and 0 otherwise.
    let mut contributions: Vec<View<i64>> = Vec::with_capacity(n);
    for (i, &v) in values.iter().enumerate() {
        let s = m.new_int_decision(0..=v.max(0));
        m.linear(s).eq(v).reified_by(dummies[i]).post()?;
        m.linear(s).eq(0).reified_by(!dummies[i]).post()?;
        contributions.push(s);
    }
    m.linear(contributions.iter().copied().sum::<IntLinearExp>())
        .eq(target)
        .post()?;

    let mut out = Out::new();
    out.put("dummies", dummies);
    Ok(out)
}
