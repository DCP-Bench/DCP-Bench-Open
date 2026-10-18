// Farmer and cows. Cow i (1..=num_cows) gives i units of milk. The farmer gives
// cows_per_son[s] cows to son s (0-based), and every son gets the same total milk.
// cow_assignments[i] is the son (0-based) that receives cow i+1.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("num_cows");
    let k = inst.size("num_sons");
    let per_son = inst.ints("cows_per_son");

    // Each cow goes to exactly one son.
    let son = m.new_int_decisions(n, 0..=(k as i64 - 1));

    // Each son receives the number of cows given by the distribution.
    for s in 0..k {
        m.linear(count_eq(&son, s as i64)).eq(per_son[s]).post()?;
    }

    // The total milk of every son is the same: the cow numbers 1..=num_cows,
    // shared equally among the sons.
    let total = (n as i64) * (n as i64 + 1) / 2;
    let milk_each = total / (k as i64);
    for s in 0..k {
        let milk: IntLinearExp = (0..n)
            .map(|i| son[i].eq(s as i64) * (i as i64 + 1))
            .sum();
        eq2(m, milk, milk_each)?;
    }

    let mut out = Out::new();
    out.put("cow_assignments", son);
    Ok(out)
}
