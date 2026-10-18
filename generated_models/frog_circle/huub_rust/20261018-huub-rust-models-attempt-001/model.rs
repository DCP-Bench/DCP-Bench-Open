// frog_circle: n cards numbered 1 to n are arranged in a circle. A frog jumps on card 1,
// then from card k it jumps k places clockwise. Find an arrangement x of the cards (x[i] is
// the card at place i, 0-based) such that the frog, starting on card 1, jumps on every card.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.int("n");
    let nu = inst.size("n");

    // Cards numbered 1 to n are arranged in a circle, each card once.
    let x = m.new_int_decisions(nu, 1..=n);
    m.unique(x.clone()).post()?;

    // The circle has no fixed first place, so the arrangement is written with card 1 first.
    m.linear(x[0]).eq(1).post()?;

    // From the card at place i, the frog jumps x[i] places clockwise, landing on place
    // (i + x[i]) mod n. next[i] is that landing place: i + x[i] = next[i] + n * wrap[i].
    let mut next = Vec::with_capacity(nu);
    for i in 0..nu {
        let s = m.new_int_decision(0..=n - 1);
        let wrap = m.new_int_decision(0..=1);
        m.linear(x[i] - s - wrap * n).eq(-(i as i64)).post()?;
        next.push(s);
    }

    // The frog starts on card 1 and must reach every place. order lists the places in the
    // order the frog visits them: order[0] holds card 1, and each jump leads to the next
    // place in the order. The last place needs no jump, since the frog stops there.
    let order = m.new_int_decisions(nu, 0..=n - 1);
    m.unique(order.clone()).post()?;
    let one = m.new_int_decision(1..=1);
    m.element(x.clone()).index(order[0]).result(one).post()?;
    for k in 0..nu - 1 {
        m.element(next.clone()).index(order[k]).result(order[k + 1]).post()?;
    }

    let mut out = Out::new();
    out.put("x", x);
    Ok(out)
}
