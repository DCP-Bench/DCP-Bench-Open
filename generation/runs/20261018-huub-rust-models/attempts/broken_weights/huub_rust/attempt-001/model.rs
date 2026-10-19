// broken_weights: a measuring weight of m pounds broke into n pieces, each a whole
// number of pounds. The pieces can weigh every integer from 1 to m on a balance,
// with pieces placed on either pan or left off. Find the weights of the pieces.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let mass = inst.int("m");
    let n = inst.size("n");

    // The pieces are whole numbers of pounds, each at least 1 pound.
    let w: Vec<_> = (0..n).map(|_| m.new_int_decision(1..=mass)).collect();

    // The pieces together weigh the whole measure.
    m.linear(w.iter().copied().sum::<IntLinearExp>()).eq(mass).post()?;

    // Every integer weight from 1 to the total can be weighed: a piece on the
    // object's pan counts +w, on the other pan -w, and off the scale 0.
    for v in 1..=mass {
        let mut signed = Vec::new();
        for i in 0..n {
            let side = m.new_int_decision(-1..=1);
            let term = m.new_int_decision(-mass..=mass);
            m.mul(side, w[i]).result(term).post()?;
            signed.push(term);
        }
        m.linear(signed.iter().copied().sum::<IntLinearExp>()).eq(v).post()?;
    }

    let mut out = Out::new();
    out.put("weights", w);
    Ok(out)
}
