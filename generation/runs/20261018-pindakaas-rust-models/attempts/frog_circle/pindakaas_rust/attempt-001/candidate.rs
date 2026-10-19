// Frog circle: cards numbered 1 to n are arranged in a circle. A frog jumps on card 1,
// then jumps to the card 1 place clockwise around the circle. From card k it jumps
// k places clockwise. Find an arrangement of cards that lets the frog jump on every card
// starting from card 1. Output x: a list of n different integers from 1 to n.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.size("n");
    let ni = n as i64;

    // Cards numbered 1 to n are arranged in a circle: x[p] is the card at position p.
    // Print the card arrangement (x) as a list of n different integers each from 1 to n.
    let mut x: Vec<IntVar> = Vec::with_capacity(n);
    for _ in 0..n {
        x.push(IntVar::new(1..=ni));
    }
    all_different(s, &x)?;

    // The frog jumps on card 1 first, so card 1 is the first card of the arrangement.
    post(s, iv(&x[0]), Comparator::Equal, 1)?;

    // From card k, the frog jumps k places clockwise: from position p it lands on
    // (p + x[p]) mod n. The position p + x[p] lies in p+1..=p+n, so a modulo gives the landing position.
    let mut nxt: Vec<IntVar> = Vec::with_capacity(n);
    for p in 0..n {
        let z = IntVar::new((p as i64 + 1)..=(p as i64 + ni));
        post(s, iv(&z) - iv(&x[p]), Comparator::Equal, p as i64)?;
        let q = IntVar::new(0..=(ni - 1));
        mod_const(s, &z, ni, &q)?;
        nxt.push(q);
    }

    // The frog jumps on every card starting from card 1: its landing positions visit all n
    // positions. Visit times ord[p] are distinct values 0..n-1, and the first position
    // (card 1) has visit time 0. Each jump goes to the next visit time, until the last one.
    let mut ord: Vec<IntVar> = Vec::with_capacity(n);
    for _ in 0..n {
        ord.push(IntVar::new(0..=(ni - 1)));
    }
    all_different(s, &ord)?;
    post(s, iv(&ord[0]), Comparator::Equal, 0)?;

    // Jump from position p lands on a position one visit time later, unless p is the last
    // one visited (visit time n-1), whose jump is not constrained.
    for p in 0..n {
        let succ = IntVar::new(0..=(ni - 1));
        element_var(s, &nxt[p], &ord, &succ)?;
        let last = reify_eq(s, iv(&ord[p]), ni - 1)?;
        post_if(s, &[!last], iv(&succ) - iv(&ord[p]), Comparator::Equal, 1)?;
    }

    let mut out = Out::new();
    out.put("x", &x);
    Ok(out)
}
