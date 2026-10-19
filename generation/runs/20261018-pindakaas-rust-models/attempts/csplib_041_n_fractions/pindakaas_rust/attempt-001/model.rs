// csplib_041_n_fractions: find distinct non-zero digits A, B, C, D, E, F, G, H, I
// such that A / BC + D / EF + G / HI = 1, where BC, EF and HI are the two-digit
// numbers formed by B and C, E and F, and H and I.
// Print the values (A, B, C, D, E, F, G, H, I) that satisfy the equation.

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

    // BC, EF and HI are the two-digit numbers formed by the digits
    let bc = define(s, scaled(&b, 10) + iv(&c))?;
    let ef = define(s, scaled(&e, 10) + iv(&f))?;
    let hi = define(s, scaled(&h, 10) + iv(&i))?;

    // Clear the denominators: multiply A/BC + D/EF + G/HI = 1 by BC * EF * HI
    // to get A * EF * HI + D * BC * HI + G * BC * EF = BC * EF * HI
    let q1 = IntVar::new(121..=9801); // EF * HI
    let q2 = IntVar::new(121..=9801); // BC * HI
    let q3 = IntVar::new(121..=9801); // BC * EF
    times(s, &ef, &hi, &q1)?;
    times(s, &bc, &hi, &q2)?;
    times(s, &bc, &ef, &q3)?;

    // BC * EF * HI
    let p = IntVar::new(1331..=970299);
    times(s, &bc, &q1, &p)?;

    // A * EF * HI, D * BC * HI and G * BC * EF
    let t1 = IntVar::new(121..=88209);
    let t2 = IntVar::new(121..=88209);
    let t3 = IntVar::new(121..=88209);
    times(s, &a, &q1, &t1)?;
    times(s, &d, &q2, &t2)?;
    times(s, &g, &q3, &t3)?;

    // The three terms add up to BC * EF * HI
    post(s, iv(&t1) + iv(&t2) + iv(&t3) - iv(&p), Comparator::Equal, 0)?;

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
