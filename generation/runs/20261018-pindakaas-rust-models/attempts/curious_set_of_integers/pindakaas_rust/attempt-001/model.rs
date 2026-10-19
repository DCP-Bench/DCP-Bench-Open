// Curious set of integers: the integers 1, 3, 8 and 120 form a set in which the product of any
// two integers is one less than a perfect square. Find a fifth number x >= 0 (x <= max_val, from
// the instance) that can be added to the set without destroying this property. Output: number.

fn is_square(t: i64) -> bool {
    let r = t.isqrt();
    r * r == t
}

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let max_val = inst.int("max_val");
    let x = IntVar::new(0..=max_val);

    // The product of any two integers is one less than a perfect square: for each member a of
    // the set, a * x is one less than a perfect square. The pairs within the set already hold.
    // A value of x that breaks one of these products is excluded.
    let set: [i64; 4] = [1, 3, 8, 120];
    for v in 0..=max_val {
        if set.iter().all(|&a| is_square(a * v + 1)) {
            continue;
        }
        let b = x.equals(s, v)?;
        let l = lit_of(s, b)?;
        s.add_clause([!l])?;
    }

    let mut out = Out::new();
    out.put("number", &x);
    Ok(out)
}
