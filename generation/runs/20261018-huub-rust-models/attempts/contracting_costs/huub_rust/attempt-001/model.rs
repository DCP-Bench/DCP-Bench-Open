// Contracting costs: a contractor planning the construction of a house pays
// certain pairs of workers a fixed amount, and asks what each man charges.
// Find the charge of the carpenter, electrician, mason, painter, paper hanger
// and plumber, in dollars, so that every stated pair payment holds.

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    let paper_hanger = m.new_int_decision(0..=5300);
    let painter = m.new_int_decision(0..=5300);
    let plumber = m.new_int_decision(0..=5300);
    let electrician = m.new_int_decision(0..=5300);
    let carpenter = m.new_int_decision(0..=5300);
    let mason = m.new_int_decision(0..=5300);

    // $ 1,100 to the paper hanger and the painter.
    eq2(m, paper_hanger + painter, 1100)?;
    // $ 1,700 to the painter and plumber.
    eq2(m, painter + plumber, 1700)?;
    // $ 1,100 to the plumber and electrician.
    eq2(m, plumber + electrician, 1100)?;
    // $ 3,300 to the electrician and carpenter.
    eq2(m, electrician + carpenter, 3300)?;
    // $ 5,300 to the carpenter and mason.
    eq2(m, carpenter + mason, 5300)?;
    // $ 3,200 to the mason and painter.
    eq2(m, mason + painter, 3200)?;

    let mut out = Out::new();
    out.put("carpenter", carpenter)
        .put("electrician", electrician)
        .put("mason", mason)
        .put("painter", painter)
        .put("paper_hanger", paper_hanger)
        .put("plumber", plumber);
    Ok(out)
}
