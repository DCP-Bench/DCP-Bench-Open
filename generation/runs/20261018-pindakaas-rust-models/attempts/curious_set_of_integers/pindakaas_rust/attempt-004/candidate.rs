// Curious set of integers: the integers 1, 3, 8 and 120 form a set in which the product of any
// two integers is one less than a perfect square. Find a fifth number x >= 0 (x <= max_val, from
// the instance) that can be added to the set without destroying this property. Output: number.

fn is_square(t: i64) -> bool {
    let r = t.isqrt();
    r * r == t
}

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let max_val = inst.int("max_val");

    // The product of any two integers is one less than a perfect square. Taking the set member 1,
    // 1 * x is one less than a perfect square, so x + 1 = r * r. The domain of x is therefore the
    // values r * r - 1 that are at most max_val, a set with about sqrt(max_val) values rather
    // than max_val + 1 of them.
    let rr = (max_val + 1).isqrt();
    let dom = pindakaas::RangeList::from_iter((1..=rr).map(|r| (r * r - 1)..=(r * r - 1)));
    let x = IntVar::new(dom);

    // For each other member a of the set, a * x is one less than a perfect square, that is
    // a * x + 1 = r * r for some r. The pairs within the set already hold.
    let set: [i64; 3] = [3, 8, 120];
    // The largest r with a * x + 1 = r * r for x <= max_val and a <= 120.
    let top = (120 * max_val + 1).isqrt();
    for &a in set.iter() {
        // r is an integer with r * r = a * x + 1, so r ranges over 0..=top.
        let r = IntVar::new(0..=top);
        for k in 0..=top {
            let t = k * k - 1;
            // r == k: a * x == k * k - 1 requires t >= 0, divisibility by a, and t / a in the
            // domain of x, that is t / a + 1 a perfect square.
            let b = r.equals(s, k)?;
            let lr = lit_of(s, b)?;
            let v = t / a;
            if t < 0 || t % a != 0 || v > max_val || !is_square(v + 1) {
                s.add_clause([!lr])?;
            } else {
                let c = x.equals(s, v)?;
                let lc = lit_of(s, c)?;
                s.add_clause([!lr, lc])?;
            }
        }
    }

    let mut out = Out::new();
    out.put("number", &x);
    Ok(out)
}
