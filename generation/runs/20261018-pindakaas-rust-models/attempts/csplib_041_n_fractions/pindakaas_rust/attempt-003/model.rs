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

fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    // Distinct non-zero digits
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

    // Products of digits, so that every product of two two-digit numbers is a
    // linear combination of digit products:
    // (10x + y)(10z + w) = 100 xz + 10 (xw + yz) + yw
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

    // q1 = EF * HI, q2 = BC * HI, q3 = BC * EF (each in 121..=9801)
    let q1 = define(s, scaled(&eh, 100) + scaled(&ei, 10) + scaled(&fh, 10) + iv(&fi))?;
    let q2 = define(s, scaled(&bh, 100) + scaled(&bi, 10) + scaled(&ch, 10) + iv(&ci))?;
    let q3 = define(s, scaled(&be, 100) + scaled(&bf, 10) + scaled(&ce, 10) + iv(&cf))?;

    // Clear the denominators: A/BC + D/EF + G/HI = 1 multiplied by BC * EF * HI
    // gives A * q1 + D * q2 + G * q3 = BC * q1, and BC * q1 = 10 B * q1 + C * q1.
    // Each product has a digit as its first factor, so the case split is on
    // the digit (9 values).
    let ta = IntVar::new(121..=88209); // A * q1
    let td = IntVar::new(121..=88209); // D * q2
    let tg = IntVar::new(121..=88209); // G * q3
    let tb = IntVar::new(121..=88209); // B * q1
    let tc = IntVar::new(121..=88209); // C * q1
    times(s, &a, &q1, &ta)?;
    times(s, &d, &q2, &td)?;
    times(s, &g, &q3, &tg)?;
    times(s, &b, &q1, &tb)?;
    times(s, &c, &q1, &tc)?;

    // A * q1 + D * q2 + G * q3 = 10 * (B * q1) + C * q1
    post(
        s,
        iv(&ta) + iv(&td) + iv(&tg) - scaled(&tb, 10) - iv(&tc),
        Comparator::Equal,
        0,
    )?;

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
