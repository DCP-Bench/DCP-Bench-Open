// Facility location: four candidate warehouses (New York, Los Angeles, Chicago, Atlanta)
// serve regional demands. Decide which warehouses to open and how many units each open
// warehouse ships to each region, to minimise the total cost (fixed costs of the opened
// warehouses plus shipping costs).

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let fixed = inst.ints("fixed_costs");
    let cost = inst.matrix("shipping_costs");
    let demands = inst.ints("demands");
    let cap = inst.int("max_shipping");
    let nw = fixed.len();
    let nr = demands.len();

    // Whether each warehouse is open: 0 or 1.
    let mut open = Vec::new();
    for _ in 0..nw {
        open.push(m.new_int_decision(0..=1));
    }

    // Units shipped from warehouse i to region j.
    let mut ship = Vec::new();
    for _ in 0..nw {
        let mut row = Vec::new();
        for _ in 0..nr {
            row.push(m.new_int_decision(0..=cap));
        }
        ship.push(row);
    }

    // Boolean view of "warehouse i is open".
    let mut ob = Vec::new();
    for i in 0..nw {
        ob.push(m.linear(open[i]).eq(1).reify());
    }

    // If the New York warehouse is opened, then the Los Angeles warehouse must also be opened.
    m.linear(open[0] - open[1]).le(0).post()?;

    // No more than three warehouses can be operational in any given week.
    m.linear(open[0] + open[1] + open[2] + open[3]).le(3).post()?;

    // Either the Atlanta or the Los Angeles warehouse must be opened.
    m.linear(open[3] + open[1]).ge(1).post()?;

    // Each open warehouse ships at most max_shipping units in total, and a closed
    // warehouse ships nothing.
    for i in 0..nw {
        let total = ship[i].iter().copied().sum::<IntLinearExp>();
        let total_zero = ship[i].iter().copied().sum::<IntLinearExp>();
        m.linear(total).le(cap).implied_by(ob[i]).post()?;
        let zero = m.linear(total_zero).le(0).reify();
        m.proposition(BoolFormula::Atom(zero) | BoolFormula::Atom(ob[i])).post()?;
    }

    // Each region receives exactly its demand.
    for j in 0..nr {
        let received = ship.iter().map(|row| row[j]).sum::<IntLinearExp>();
        m.linear(received).eq(demands[j]).post()?;
    }

    // Total cost: fixed costs of the opened warehouses plus shipping costs.
    let mut ub: i64 = fixed.iter().sum();
    for j in 0..nr {
        let mx = (0..nw).map(|i| cost[i][j]).max().unwrap_or(0);
        ub += demands[j] * mx;
    }
    let obj = m.new_int_decision(0..=ub);
    let s = &ship;
    let c = &cost;
    let terms = (0..nw)
        .map(|i| open[i] * fixed[i])
        .chain((0..nw).flat_map(|i| (0..nr).map(move |j| s[i][j] * c[i][j])))
        .sum::<IntLinearExp>();
    m.linear(terms).eq(obj).post()?;

    let mut out = Out::new();
    out.put("open_warehouse", ob).put("ships", ship).put("total_cost", obj);
    out.minimise(obj);
    Ok(out)
}
