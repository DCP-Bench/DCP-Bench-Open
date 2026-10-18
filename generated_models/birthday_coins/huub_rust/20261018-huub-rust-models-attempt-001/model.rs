// Birthday coins: Tommy was given 15 coins for his birthday (half-crowns,
// shillings and sixpence) and found that he had 1 pound 5 shillings and 6 pence.
// Question: how many half-crowns was he given?
// Units: pence. A half-crown is 30d, a shilling 12d, a sixpence 6d, and the total is 306d.

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    // Tommy was given 15 coins for his birthday (half-crowns, shillings and sixpence).
    // Each of the three kinds of coin is among them.
    let half_crowns = m.new_int_decision(1..=15);
    let shillings = m.new_int_decision(1..=15);
    let sixpences = m.new_int_decision(1..=15);
    m.linear(half_crowns + shillings + sixpences).eq(15).post()?;

    // He found that he had 1 pound 5 shillings and 6 pence, that is 306 pence.
    // A half-crown is 2 shillings and sixpence (30 pence), a shilling is 12 pence,
    // and a sixpence is 6 pence.
    m.linear(half_crowns * 30 + shillings * 12 + sixpences * 6)
        .eq(306)
        .post()?;

    let mut out = Out::new();
    out.put("half_crowns", half_crowns);
    Ok(out)
}
