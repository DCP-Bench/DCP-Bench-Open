// Hanging weights puzzle: thirteen weights A..M, each an integer in 1..=13, hang from a
// system of bars. The weights must balance: on either side of each pivot, the weights
// times their distance from the pivot are equal. A bar hanging beneath another contributes
// its total weight as if it were a single weight at the point where it attaches.

// Sum of coefficient * variable, as one linear expression.
fn lin(ts: &[(&IntVar, i64)]) -> LinExp {
    let mut e = LinExp::default();
    for (x, c) in ts {
        e += scaled(x, *c);
    }
    e
}

fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let a = IntVar::new(1..=13);
    let b = IntVar::new(1..=13);
    let c = IntVar::new(1..=13);
    let d = IntVar::new(1..=13);
    let e = IntVar::new(1..=13);
    let f = IntVar::new(1..=13);
    let g = IntVar::new(1..=13);
    let h = IntVar::new(1..=13);
    let i = IntVar::new(1..=13);
    let j = IntVar::new(1..=13);
    let k = IntVar::new(1..=13);
    let l = IntVar::new(1..=13);
    let m = IntVar::new(1..=13);

    // The weights in the puzzle have distinct values.
    all_different(s, &[a.clone(), b.clone(), c.clone(), d.clone(), e.clone(), f.clone(), g.clone(), h.clone(), i.clone(), j.clone(), k.clone(), l.clone(), m.clone()])?;

    // The top bar: the bar carrying L and M (with everything under it) hangs at distance 4
    // on the left, and the bar carrying J and K (with everything under it) hangs at distance 3
    // on the right. The weights on either side of the pivot are equal when weighted by distance.
    post(
        s,
        lin(&[(&l, 4), (&m, 4), (&h, 4), (&i, 4), (&e, 4), (&f, 4),
              (&j, -3), (&k, -3), (&g, -3), (&a, -3), (&b, -3), (&c, -3), (&d, -3)]),
        Comparator::Equal,
        0,
    )?;

    // The bar carrying L and M: the bar with H, I, E, F hangs at distance 1 on the left;
    // L is at distance 1 on the right and M at distance 4. A bar hanging beneath another
    // contributes its total weight as if it were a single weight.
    post(
        s,
        lin(&[(&h, 1), (&i, 1), (&e, 1), (&f, 1), (&l, -1), (&m, -4)]),
        Comparator::Equal,
        0,
    )?;

    // The bar carrying H and I: H is at distance 3 on the left; the bar carrying E and F
    // is at distance 2 and I at distance 3 on the right.
    post(
        s,
        lin(&[(&h, 3), (&e, -2), (&f, -2), (&i, -3)]),
        Comparator::Equal,
        0,
    )?;

    // The bar carrying E and F: E is at distance 3 on the left and F at distance 2 on the right.
    // This gives 3*E = 2*F.
    post(
        s,
        lin(&[(&e, 3), (&f, -2)]),
        Comparator::Equal,
        0,
    )?;

    // The bar carrying J and K: the bar carrying A and B is at distance 3 and J at distance 2
    // on the left; K is at distance 1 and the bar carrying G, C and D at distance 2 on the right.
    // The bar hanging beneath counts as its total weight.
    post(
        s,
        lin(&[(&a, 3), (&b, 3), (&j, 2), (&k, -1), (&g, -2), (&c, -2), (&d, -2)]),
        Comparator::Equal,
        0,
    )?;

    // The bar carrying A and B: A is at distance 4 on the left and B at distance 1 on the right.
    // This gives 4*A = B.
    post(
        s,
        lin(&[(&a, 4), (&b, -1)]),
        Comparator::Equal,
        0,
    )?;

    // The bar carrying G: G is at distance 3 on the left; the bar carrying C and D is at
    // distance 2 on the right. The bar hanging beneath counts as its total weight, so
    // 3*G = 2*(C+D).
    post(
        s,
        lin(&[(&g, 3), (&c, -2), (&d, -2)]),
        Comparator::Equal,
        0,
    )?;

    // The bottom right bar: C is at distance 5 on the left and D at distance 1 on the right,
    // so 5*C = D.
    post(
        s,
        lin(&[(&c, 5), (&d, -1)]),
        Comparator::Equal,
        0,
    )?;

    let mut out = Out::new();
    out.put("a", &a)
        .put("b", &b)
        .put("c", &c)
        .put("d", &d)
        .put("e", &e)
        .put("f", &f)
        .put("g", &g)
        .put("h", &h)
        .put("i", &i)
        .put("j", &j)
        .put("k", &k)
        .put("l", &l)
        .put("m", &m);
    Ok(out)
}
