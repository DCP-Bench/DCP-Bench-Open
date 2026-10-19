// Contracting costs: a contractor pays pairs of workers a fixed sum for the
// work each pair does together. Find what each of the six men charges:
// paper hanger, painter, plumber, electrician, carpenter, mason (in dollars).
// The instance carries no fields; the amounts are the problem's own data.

fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    // Each charge is a non-negative amount of dollars, and no charge can exceed
    // the largest payment in the statement (5,300).
    let max_charge = 5300;
    let paper_hanger = IntVar::new(0..=max_charge);
    let painter = IntVar::new(0..=max_charge);
    let plumber = IntVar::new(0..=max_charge);
    let electrician = IntVar::new(0..=max_charge);
    let carpenter = IntVar::new(0..=max_charge);
    let mason = IntVar::new(0..=max_charge);

    // $1,100 to the paper hanger and the painter
    post(s, iv(&paper_hanger) + iv(&painter), Comparator::Equal, 1100)?;
    // $1,700 to the painter and plumber
    post(s, iv(&painter) + iv(&plumber), Comparator::Equal, 1700)?;
    // $1,100 to the plumber and electrician
    post(s, iv(&plumber) + iv(&electrician), Comparator::Equal, 1100)?;
    // $3,300 to the electrician and carpenter
    post(s, iv(&electrician) + iv(&carpenter), Comparator::Equal, 3300)?;
    // $5,300 to the carpenter and mason
    post(s, iv(&carpenter) + iv(&mason), Comparator::Equal, 5300)?;
    // $3,200 to the mason and painter
    post(s, iv(&mason) + iv(&painter), Comparator::Equal, 3200)?;

    let mut out = Out::new();
    out.put("carpenter", &carpenter)
        .put("electrician", &electrician)
        .put("mason", &mason)
        .put("painter", &painter)
        .put("paper_hanger", &paper_hanger)
        .put("plumber", &plumber);
    Ok(out)
}
