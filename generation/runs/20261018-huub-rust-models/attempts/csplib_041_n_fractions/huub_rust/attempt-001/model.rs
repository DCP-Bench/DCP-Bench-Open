// csplib_041_n_fractions: find distinct non-zero digits A, B, C, D, E, F, G, H, I
// such that A / BC + D / EF + G / HI = 1, where BC, EF and HI are two-digit
// numbers formed by B and C, E and F, and H and I.

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    // Find distinct non-zero digits.
    let a = m.new_int_decision(1..=9);
    let b = m.new_int_decision(1..=9);
    let c = m.new_int_decision(1..=9);
    let d = m.new_int_decision(1..=9);
    let e = m.new_int_decision(1..=9);
    let f = m.new_int_decision(1..=9);
    let g = m.new_int_decision(1..=9);
    let h = m.new_int_decision(1..=9);
    let i = m.new_int_decision(1..=9);
    m.unique(vec![a, b, c, d, e, f, g, h, i]).post()?;

    // BC, EF and HI are two-digit numbers formed by B and C, E and F, and H and I.
    let bc = m.new_int_decision(10..=99);
    let ef = m.new_int_decision(10..=99);
    let hi = m.new_int_decision(10..=99);
    m.linear(b * 10 + c).eq(bc).post()?;
    m.linear(e * 10 + f).eq(ef).post()?;
    m.linear(h * 10 + i).eq(hi).post()?;

    // A / BC + D / EF + G / HI = 1, multiplied out by BC * EF * HI:
    // A * EF * HI + D * BC * HI + G * BC * EF = BC * EF * HI.
    let ef_hi = m.new_int_decision(100..=9801);
    let bc_hi = m.new_int_decision(100..=9801);
    let bc_ef = m.new_int_decision(100..=9801);
    let bc_ef_hi = m.new_int_decision(1000..=970299);
    m.mul(ef, hi).result(ef_hi).post()?;
    m.mul(bc, hi).result(bc_hi).post()?;
    m.mul(bc, ef).result(bc_ef).post()?;
    m.mul(bc, ef_hi).result(bc_ef_hi).post()?;

    let t1 = m.new_int_decision(1..=88209);
    let t2 = m.new_int_decision(1..=88209);
    let t3 = m.new_int_decision(1..=88209);
    m.mul(a, ef_hi).result(t1).post()?;
    m.mul(d, bc_hi).result(t2).post()?;
    m.mul(g, bc_ef).result(t3).post()?;

    // The three weighted fractions sum to the product.
    m.linear(t1 + t2 + t3).eq(bc_ef_hi).post()?;

    let mut out = Out::new();
    out.put("A", a)
        .put("B", b)
        .put("C", c)
        .put("D", d)
        .put("E", e)
        .put("F", f)
        .put("G", g)
        .put("H", h)
        .put("I", i);
    Ok(out)
}
