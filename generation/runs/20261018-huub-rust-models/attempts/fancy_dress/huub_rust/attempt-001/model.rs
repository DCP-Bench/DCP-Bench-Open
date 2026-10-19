// Fancy dress party (Mr Greenguest): choose which of tie (t), hat (h), shirt (r),
// socks (s) to wear in green, and whether to pay the entrance fee (n), so that the
// total cost is minimal. Costs: tie 10, hat 2, socks 12, entrance fee 11. The shirt
// is already owned, so wearing it costs nothing.
// Each rule below must hold unless the guest pays the entrance fee (n = 1).

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    // 0/1 decisions for the choices; their Boolean views are the declared outputs.
    let t = m.new_int_decision(0..=1);
    let h = m.new_int_decision(0..=1);
    let r = m.new_int_decision(0..=1);
    let s = m.new_int_decision(0..=1);
    let n = m.new_int_decision(0..=1);

    // The guest who does not pay the entrance fee (n = 0) must follow rules 1-3.
    let paid_free = n.eq(0);

    // 1 If someone wears a green tie he has to wear a green shirt.
    m.linear(t - r).le(0).implied_by(paid_free).post()?;

    // 2 A guest may only wear green socks and a green shirt if he wears a green tie
    //   or a green hat.
    m.linear(s + r - t - h).le(1).implied_by(paid_free).post()?;

    // 3 A guest wearing a green shirt or a green hat or who does not wear green
    //   socks must wear a green tie.
    //   Clauses: (not r or t), (not h or t), (s or t).
    m.linear(r - t).le(0).implied_by(paid_free).post()?;
    m.linear(h - t).le(0).implied_by(paid_free).post()?;
    m.linear(s + t).ge(1).implied_by(paid_free).post()?;

    // Cost: 10 tie + 2 hat + 12 socks + 11 entrance fee, to be minimised.
    let cost = m.new_int_decision(0..=100);
    m.linear(t * 10 + h * 2 + s * 12 + n * 11).eq(cost).post()?;

    let mut out = Out::new();
    out.put("t", t.eq(1))
        .put("h", h.eq(1))
        .put("r", r.eq(1))
        .put("s", s.eq(1))
        .put("n", n.eq(1));
    out.minimise(cost);
    Ok(out)
}
