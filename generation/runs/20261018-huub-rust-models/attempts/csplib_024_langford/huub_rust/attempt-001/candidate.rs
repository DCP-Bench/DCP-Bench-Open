// Langford's problem (csplib 024), for one instance with field k.
// Two sets of the numbers 1 to k form one sequence of 2k numbers in which the two 1's
// are one number apart, the two 2's two numbers apart, ..., and the two k's k numbers apart.
// Output sol is that sequence of 2k integers from 1 to k.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let k = inst.int("k");
    let n = 2 * k;

    // The two copies of each number i sit at positions a_i and b_i (0-based).
    // The two i's appear i numbers apart, so the second copy is i + 1 positions after the first.
    let mut first: Vec<View<i64>> = Vec::new();
    let mut second: Vec<View<i64>> = Vec::new();
    for i in 1..=k {
        let a = m.new_int_decision(0..=n - 1);
        let b = m.new_int_decision(0..=n - 1);
        eq2(m, b - a, i + 1)?;
        first.push(a);
        second.push(b);
    }

    // The 2k positions hold the 2k numbers, one each.
    let mut positions: Vec<View<i64>> = Vec::new();
    positions.extend(first.iter().copied());
    positions.extend(second.iter().copied());
    m.unique(positions).post()?;

    // Output sol: the number whose copy sits at position j.
    // If a copy of i is at position j, then sol[j] is i.
    let sol: Vec<View<i64>> = (0..n).map(|_| m.new_int_decision(1..=k)).collect();
    for i in 1..=k {
        let idx = (i - 1) as usize;
        for j in 0..n {
            let at_a = m.linear(first[idx]).eq(j).reify();
            m.linear(sol[j as usize]).eq(i).implied_by(at_a).post()?;
            let at_b = m.linear(second[idx]).eq(j).reify();
            m.linear(sol[j as usize]).eq(i).implied_by(at_b).post()?;
        }
    }

    let mut out = Out::new();
    out.put("sol", sol);
    Ok(out)
}
