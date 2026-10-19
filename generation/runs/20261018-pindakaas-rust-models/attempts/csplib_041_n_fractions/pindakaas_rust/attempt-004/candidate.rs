// csplib_041_n_fractions: find distinct non-zero digits A, B, C, D, E, F, G, H, I
// such that A / BC + D / EF + G / HI = 1, where BC, EF and HI are the two-digit
// numbers formed by B and C, E and F, and H and I.
// Print the values (A, B, C, D, E, F, G, H, I) that satisfy the equation.

// The product of two digits, as a fresh variable (values 1..=81).
fn digit_product(s: &mut Cadical, x: &IntVar, y: &IntVar) -> Res<IntVar> {
    let z = IntVar::new(1..=81);
    times(s, x, y, &z)?;
    Ok(z)
}

// The product of a digit and a digit product, as a fresh variable (1..=729).
fn triple_product(s: &mut Cadical, x: &IntVar, p: &IntVar) -> Res<IntVar> {
    let z = IntVar::new(1..=729);
    times(s, x, p, &z)?;
    Ok(z)
}

fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    // Find distinct non-zero digits: all nine variables take values 1..9 and differ
    let a = IntVar::new(1..=9);
    let b = IntVar::new(1..=9);
    let c = IntVar::new(1..=9);
    let d = IntVar::new(1..=9);
    let e = IntVar::new(1..=9);
    let f = IntVar::new(1..=9);
    let g = IntVar::new(1..=9);
    let h = IntVar::new(1..=9);
    let i = IntVar::new(1..=9);
    let digits = vec![
        a.clone(), b.clone(), c.clone(), d.clone(), e.clone(),
        f.clone(), g.clone(), h.clone(), i.clone(),
    ];
    all_different(s, &digits)?;

    // Products of two digits
    let bh = digit_product(s, &b, &h)?;
    let bi = digit_product(s, &b, &i)?;
    let ch = digit_product(s, &c, &h)?;
    let ci = digit_product(s, &c, &i)?;
    let be = digit_product(s, &b, &e)?;
    let bf = digit_product(s, &b, &f)?;
    let ce = digit_product(s, &c, &e)?;
    let cf = digit_product(s, &c, &f)?;
    let eh = digit_product(s, &e, &h)?;
    let ei = digit_product(s, &e, &i)?;
    let fh = digit_product(s, &f, &h)?;
    let fi = digit_product(s, &f, &i)?;

    // A / BC + D / EF + G / HI = 1, multiplied by BC * EF * HI:
    // A * EF * HI + D * BC * HI + G * BC * EF = BC * EF * HI.
    // With BC = 10B + C, EF = 10E + F, HI = 10H + I, every term is a sum of
    // digit triples, so each product is a variable with a small domain.
    // A * EF * HI
    let aeh = triple_product(s, &a, &eh)?;
    let aei = triple_product(s, &a, &ei)?;
    let afh = triple_product(s, &a, &fh)?;
    let afi = triple_product(s, &a, &fi)?;
    // D * BC * HI
    let dbh = triple_product(s, &d, &bh)?;
    let dbi = triple_product(s, &d, &bi)?;
    let dch = triple_product(s, &d, &ch)?;
    let dci = triple_product(s, &d, &ci)?;
    // G * BC * EF
    let gbe = triple_product(s, &g, &be)?;
    let gbf = triple_product(s, &g, &bf)?;
    let gce = triple_product(s, &g, &ce)?;
    let gcf = triple_product(s, &g, &cf)?;
    // BC * EF * HI = (10B + C) * EF * HI
    let beh = triple_product(s, &b, &eh)?;
    let bei = triple_product(s, &b, &ei)?;
    let bfh = triple_product(s, &b, &fh)?;
    let bfi = triple_product(s, &b, &fi)?;
    let ceh = triple_product(s, &c, &eh)?;
    let cei = triple_product(s, &c, &ei)?;
    let cfh = triple_product(s, &c, &fh)?;
    let cfi = triple_product(s, &c, &fi)?;

    // A / BC + D / EF + G / HI = 1, cleared of denominators, with
    // A * EF * HI = 100 aeh + 10 aei + 10 afh + afi, and similarly for the others
    let lhs = scaled(&aeh, 100) + scaled(&aei, 10) + scaled(&afh, 10) + iv(&afi)
        + scaled(&dbh, 100) + scaled(&dbi, 10) + scaled(&dch, 10) + iv(&dci)
        + scaled(&gbe, 100) + scaled(&gbf, 10) + scaled(&gce, 10) + iv(&gcf);
    let rhs = scaled(&beh, 1000) + scaled(&bei, 100) + scaled(&bfh, 100) + scaled(&bfi, 10)
        + scaled(&ceh, 100) + scaled(&cei, 10) + scaled(&cfh, 10) + iv(&cfi);
    post(s, lhs - rhs, Comparator::Equal, 0)?;

    let mut out = Out::new();
    out.put("A", &a)
        .put("B", &b)
        .put("C", &c)
        .put("D", &d)
        .put("E", &e)
        .put("F", &f)
        .put("G", &g)
        .put("H", &h)
        .put("I", &i);
    Ok(out)
}
