// Aircraft assignment: assign aircraft of several types to routes so that every
// route's passenger demand is met, the aircraft of each type do not exceed its
// availability, and the total operational cost is minimised.
// allocation[i][j] is the number of aircraft of type i assigned to route j.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let availability = inst.ints("availability");
    let demand = inst.ints("demand");
    let capabilities = inst.matrix("capabilities");
    let costs = inst.matrix("costs");
    let types = availability.len();
    let routes = demand.len();

    // Each allocation[i][j] is a non-negative integer, at most the availability of type i.
    let mut allocation: Vec<Vec<View<i64>>> = Vec::with_capacity(types);
    for i in 0..types {
        let mut row: Vec<View<i64>> = Vec::with_capacity(routes);
        for _j in 0..routes {
            row.push(m.new_int_decision(0..=availability[i]));
        }
        allocation.push(row);
    }

    // The aircraft assigned to a route must carry its passenger demand.
    for j in 0..routes {
        let seats: IntLinearExp = (0..types)
            .map(|i| allocation[i][j] * capabilities[i][j])
            .sum();
        m.linear(seats).ge(demand[j]).post()?;
    }

    // The aircraft of each type, over all routes, must not exceed its availability.
    for i in 0..types {
        let used: IntLinearExp = (0..routes).map(|j| allocation[i][j]).sum();
        m.linear(used).le(availability[i]).post()?;
    }

    // The objective is the total operational cost of the assignment.
    let max_cost: i64 = (0..types)
        .map(|i| (0..routes).map(|j| costs[i][j] * availability[i]).sum::<i64>())
        .sum();
    let total = m.new_int_decision(0..=max_cost);
    let cost: IntLinearExp = (0..types)
        .flat_map(|i| (0..routes).map(move |j| (i, j)))
        .map(|(i, j)| allocation[i][j] * costs[i][j])
        .sum();
    m.linear(cost).eq(total).post()?;

    let mut out = Out::new();
    out.put("allocation", allocation);
    out.minimise(total);
    Ok(out)
}
