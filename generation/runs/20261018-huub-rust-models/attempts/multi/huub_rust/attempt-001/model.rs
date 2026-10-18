// Multi-commodity transportation problem: origins ship products to destinations.
// Shipping one unit of product p from origin i to destination j costs cost[i][j][p].
// Minimise the total shipping cost (total_cost).

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let supply = inst.matrix("supply");
    let demand = inst.matrix("demand");
    let limit = inst.matrix("limit");
    let cost = inst.cube("cost");
    let origins = supply.len();
    let destinations = demand.len();
    let products = supply[0].len();

    // Units of product p shipped from origin i to destination j.
    // Each is bounded by the smallest of the supply, the demand and the lane limit.
    let mut x: Vec<Vec<Vec<View<i64>>>> = Vec::new();
    let mut max_total: i64 = 0;
    for i in 0..origins {
        let mut row = Vec::new();
        for j in 0..destinations {
            let mut lane = Vec::new();
            for p in 0..products {
                let ub = supply[i][p].min(demand[j][p]).min(limit[i][j]);
                max_total += ub * cost[i][j][p];
                lane.push(m.new_int_decision(0..=ub));
            }
            row.push(lane);
        }
        x.push(row);
    }

    // Each origin ships at most its supply of each product.
    for i in 0..origins {
        for p in 0..products {
            let shipped: IntLinearExp = (0..destinations)
                .map(|j| IntLinearExp::from(x[i][j][p]))
                .sum();
            m.linear(shipped).le(supply[i][p]).post()?;
        }
    }

    // Each lane from an origin to a destination carries at most its limit, over all products.
    for i in 0..origins {
        for j in 0..destinations {
            let lane: IntLinearExp = (0..products)
                .map(|p| IntLinearExp::from(x[i][j][p]))
                .sum();
            m.linear(lane).le(limit[i][j]).post()?;
        }
    }

    // Each destination receives exactly its demand of each product.
    for j in 0..destinations {
        for p in 0..products {
            let received: IntLinearExp = (0..origins)
                .map(|i| IntLinearExp::from(x[i][j][p]))
                .sum();
            eq2(m, received, demand[j][p])?;
        }
    }

    // The total cost is the unit cost times the quantity, summed over all shipments.
    let mut cost_terms: Vec<IntLinearExp> = Vec::new();
    for i in 0..origins {
        for j in 0..destinations {
            for p in 0..products {
                cost_terms.push((x[i][j][p] * cost[i][j][p]).into());
            }
        }
    }
    let total_cost_expr: IntLinearExp = cost_terms.into_iter().sum();
    let total = m.new_int_decision(0..=max_total);
    m.linear(total_cost_expr).eq(total).post()?;

    let mut out = Out::new();
    out.put("total_cost", total);
    out.minimise(total);
    Ok(out)
}
