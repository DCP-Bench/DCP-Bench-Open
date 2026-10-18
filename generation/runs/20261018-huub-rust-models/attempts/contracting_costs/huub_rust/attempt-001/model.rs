// Contracting costs: a contractor planning the construction of a house pays
// certain pairs of workers a fixed amount, and asks what each man charges.
// Find the charge of the carpenter, electrician, mason, painter, paper hanger
// and plumber, in dollars, so that every stated pair payment holds.

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    let paper_hanger = m.new_int_decision(0..=10000);
    let painter = m.new_int_decision(0..=10000);
    let plumber = m.new_int_decision(0..=10000);
    let electrician = m.new_int_decision(0..=10000);
    let carpenter = m.new_int_decision(0..=10000);
    let mason = m.new_int_decision(0..=10000);

    // $ 1,100 to the paper hanger and the painter.
    m.linear(paper_hanger + painter).eq(1100).post()?;
    // $ 1,700 to the painter and plumber.
    m.linear(painter + plumber).eq(1700).post()?;
    // $ 1,100 to the plumber and electrician.
    m.linear(plumber + electrician).eq(1100).post()?;
    // $ 3,300 to the electrician and carpenter.
    m.linear(electrician + carpenter).eq(3300).post()?;
    // $ 5,300 to the carpenter and mason.
    m.linear(carpenter + mason).eq(5300).post()?;
    // $ 3,200 to the mason and painter.
    m.linear(mason + painter).eq(3200).post()?;

    let mut out = Out::new();
    out.put("carpenter", carpenter)
        .put("electrician", electrician)
        .put("mason", mason)
        .put("painter", painter)
        .put("paper_hanger", paper_hanger)
        .put("plumber", plumber);
    Ok(out)
}
