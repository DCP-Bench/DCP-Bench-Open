// Ages of the three sons (ages_of_the_sons). Outputs A1, A2, A3 are the ages, oldest first.

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    // The sons' ages: whole numbers, listed from the oldest.
    let a1 = m.new_int_decision(1..=36);
    let a2 = m.new_int_decision(1..=36);
    let a3 = m.new_int_decision(1..=36);
    m.linear(a2).le(a1).post()?;
    m.linear(a3).le(a2).post()?;

    // "The product of their ages is 36."
    let p = m.new_int_decision(1..=1296);
    m.mul(a1, a2).result(p).post()?;
    let product = m.new_int_decision(36..=36);
    m.mul(p, a3).result(product).post()?;

    // "The sum of their ages equals the number of the windows in that building."
    // The number of windows is unknown, so it is a free variable s.
    let s = m.new_int_decision(3..=108);
    m.linear(a1 + a2 + a3).eq(s).post()?;

    // "After a short while the mathematician said: I need more information."
    // Another set of ages with product 36 and the same sum must exist, and it must differ from (a1, a2, a3).
    let b1 = m.new_int_decision(1..=36);
    let b2 = m.new_int_decision(1..=36);
    let b3 = m.new_int_decision(1..=36);
    m.linear(b2).le(b1).post()?;
    m.linear(b3).le(b2).post()?;
    let pb = m.new_int_decision(1..=1296);
    m.mul(b1, b2).result(pb).post()?;
    let productb = m.new_int_decision(36..=36);
    m.mul(pb, b3).result(productb).post()?;
    m.linear(b1 + b2 + b3).eq(s).post()?;
    // The other ages differ from ours in at least one son.
    let d1 = m.linear(b1).ne(a1).reify();
    let d2 = m.linear(b2).ne(a2).reify();
    let d3 = m.linear(b3).ne(a3).reify();
    m.proposition(BoolFormula::Atom(d1) | BoolFormula::Atom(d2) | BoolFormula::Atom(d3))
        .post()?;

    // "The oldest son has blue eyes." "I got it." The oldest son is a single son.
    m.linear(a1).gt(a2).post()?;

    let mut out = Out::new();
    out.put("A1", a1).put("A2", a2).put("A3", a3);
    Ok(out)
}
