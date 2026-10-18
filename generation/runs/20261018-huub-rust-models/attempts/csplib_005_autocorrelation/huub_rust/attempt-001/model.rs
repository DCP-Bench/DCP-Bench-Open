// csplib_005_autocorrelation: a binary sequence S of length n, each bit +1 or -1,
// that minimises the sum of squared periodic autocorrelations
// E = sum_{k=1}^{n-1} C_k^2, where C_k = sum_{i=0}^{n-1} S_i * S_{(i+k) mod n}.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("n");
    let ni = n as i64;

    // The bits take the value +1 or -1.
    let s: Vec<View<i64>> = (0..n).map(|_| m.new_int_decision(-1..=1)).collect();
    for i in 0..n {
        m.linear(s[i]).ne(0).post()?;
    }

    // The k-th periodic autocorrelation C_k is the sum over i of S_i * S_{(i+k) mod n}.
    // Each product of two bits is a view in -1..=1.
    let mut sq: Vec<View<i64>> = Vec::new();
    for k in 1..n {
        let mut prods: Vec<View<i64>> = Vec::new();
        for i in 0..n {
            let j = (i + k) % n;
            let p = m.new_int_decision(-1..=1);
            m.mul(s[i], s[j]).result(p).post()?;
            prods.push(p);
        }
        let c = m.new_int_decision(-ni..=ni);
        m.linear(prods.iter().copied().sum::<IntLinearExp>()).eq(c).post()?;

        // The squared autocorrelation C_k^2.
        let c2 = m.new_int_decision(0..=ni * ni);
        m.mul(c, c).result(c2).post()?;
        sq.push(c2);
    }

    // The energy E is the sum of the squared autocorrelations, to be minimised.
    let energy = m.new_int_decision(0..=(ni - 1) * ni * ni);
    m.linear(sq.iter().copied().sum::<IntLinearExp>()).eq(energy).post()?;

    let mut out = Out::new();
    out.put("sequence", s);
    out.minimise(energy);
    Ok(out)
}
