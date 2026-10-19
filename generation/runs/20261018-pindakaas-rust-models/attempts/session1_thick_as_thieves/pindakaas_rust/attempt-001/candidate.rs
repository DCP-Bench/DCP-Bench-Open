// Thick as thieves (session1): six suspects, artie, bill, crackitt, dodgy, edgy, fingers.
// Each suspect is guilty or not. The getaway car was barely big enough to hold two, so at
// least four are innocent: at most two are guilty. The innocent tell the truth, the guilty
// lie. Each statement must therefore be true exactly when its speaker is innocent.

fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    // Guilt literals: true when the suspect is guilty.
    let a = s.new_lit(); // artie
    let b = s.new_lit(); // bill
    let c = s.new_lit(); // crackitt
    let d = s.new_lit(); // dodgy
    let e = s.new_lit(); // edgy
    let f = s.new_lit(); // fingers

    // At least four of them were innocent, so at most two are guilty.
    let mut guilty = LinExp::default();
    guilty += LinExp::from(a);
    guilty += LinExp::from(b);
    guilty += LinExp::from(c);
    guilty += LinExp::from(d);
    guilty += LinExp::from(e);
    guilty += LinExp::from(f);
    post(s, guilty.clone(), Comparator::LessEq, 2)?;

    // Artie: "It wasn't me." The statement is "not artie guilty", which is true exactly
    // when artie is innocent. This holds for any value of a, so no constraint is needed.

    // Bill: "Crackitt was in it up to his neck." The statement is c. It must be true
    // exactly when bill is innocent: c <-> not b.
    s.add_clause([c, b])?;
    s.add_clause([!c, !b])?;

    // Crackitt: "No I wasn't." The statement is "not c", which is true exactly when
    // crackitt is innocent. This holds for any value of c, so no constraint is needed.

    // Dodgy: "If Crackitt did it, Bill did it with him." The statement is (c -> b). It must
    // be true exactly when dodgy is innocent: (c -> b) <-> not d.
    s.add_clause([c, !d])?;
    s.add_clause([!b, !d])?;
    s.add_clause([d, !c, b])?;

    // Edgy: "Nobody did it alone." The statement is that the number of guilty is not one.
    // Let q be "exactly one guilty". The statement is not q, which must be true exactly
    // when edgy is innocent: not q <-> not e, so q <-> e.
    let q = reify_eq(s, guilty.clone(), 1)?;
    s.add_clause([!q, e])?;
    s.add_clause([q, !e])?;

    // Fingers: "That's right: it was Artie and Dodgy together." The statement t is that
    // artie and dodgy are guilty and the other suspects other than fingers are not:
    // t <-> (a and d and not b and not c and not e). It must be true exactly when fingers
    // is innocent: t <-> not f.
    let t = s.new_lit();
    s.add_clause([!t, a])?;
    s.add_clause([!t, d])?;
    s.add_clause([!t, !b])?;
    s.add_clause([!t, !c])?;
    s.add_clause([!t, !e])?;
    s.add_clause([t, !a, !d, b, c, e])?;
    s.add_clause([!t, !f])?;
    s.add_clause([t, f])?;

    let mut out = Out::new();
    out.put("artie", a)
        .put("bill", b)
        .put("crackitt", c)
        .put("dodgy", d)
        .put("edgy", e)
        .put("fingers", f);
    Ok(out)
}
