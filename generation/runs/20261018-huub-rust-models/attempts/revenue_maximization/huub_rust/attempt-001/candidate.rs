// Revenue maximization: choose how many units of each itinerary package to sell.
// Each package uses some flight legs (delta[package][leg] == 1). Each leg has a limited
// number of passenger seats (available_seats). The packages are sold as units, and the
// units sold must fit in the seats of every leg they use.
// Each package sells at most its estimated demand.
// Maximize the total revenue, the sum of revenue[package] * units sold of that package.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let demand = inst.ints("demand");
    let revenue = inst.ints("revenue");
    let seats = inst.ints("available_seats");
    let delta = inst.matrix("delta");
    let np = demand.len();
    let nl = seats.len();

    // Units of each package to sell, between 0 and its demand.
    let mut units: Vec<View<i64>> = Vec::new();
    for j in 0..np {
        units.push(m.new_int_decision(0..=demand[j]));
    }

    // We reserve the passenger seats according to the number of packages we want to sell:
    // on each leg, the units of all packages using that leg fit in its seats.
    for l in 0..nl {
        let users: Vec<View<i64>> = (0..np).filter(|&j| delta[j][l] == 1).map(|j| units[j]).collect();
        if users.is_empty() {
            continue;
        }
        m.linear(users.iter().copied().sum::<IntLinearExp>()).le(seats[l]).post()?;
    }

    // Maximize the total revenue from the units sold.
    let max_rev: i64 = (0..np).map(|j| revenue[j] * demand[j]).sum();
    let total = m.new_int_decision(0..=max_rev);
    let rev_terms: Vec<IntLinearExp> = (0..np).map(|j| (units[j] * revenue[j]).into()).collect();
    m.linear(rev_terms.into_iter().sum::<IntLinearExp>()).eq(total).post()?;

    let mut out = Out::new();
    out.put("packages_to_sell", units).put("max_revenue", total);
    out.maximise(total);
    Ok(out)
}
