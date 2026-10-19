// Multi-commodity transportation problem: origins ship products to destinations.
// Shipping one unit of product p from origin i to destination j costs cost[i][j][p].
// Minimise the total shipping cost (total_cost).
//
// Attempt 002: the same constraints as attempt 001, plus a cost variable per
// (destination, product) with tight bounds, so the optimum is bounded per demand.

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
    let mut ub = vec![vec![vec![0i64; products]; destinations]; origins];
    let mut x: Vec<Vec<Vec<View<i64>>>> = Vec::new();
    for i in 0..origins {
        let mut row = Vec::new();
        for j in 0..destinations {
            let mut lane = Vec::new();
            for p in 0..products {
                let u = supply[i][p].min(demand[j][p]).min(limit[i][j]);
                ub[i][j][p] = u;
                lane.push(m.new_int_decision(0..=u));
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

    // The cost of the shipments that deliver product p to destination j.
    // Its bounds follow from the demand and the cheapest and dearest unit cost.
    let mut total_lo: i64 = 0;
    let mut total_hi: i64 = 0;
    let mut pair_costs: Vec<View<i64>> = Vec::new();
    for j in 0..destinations {
        for p in 0..products {
            let mut lo_unit = i64::MAX;
            let mut hi_cost: i64 = 0;
            let mut terms: Vec<IntLinearExp> = Vec::new();
            for i in 0..origins {
                lo_unit = lo_unit.min(cost[i][j][p]);
                hi_cost += ub[i][j][p] * cost[i][j][p];
                terms.push((x[i][j][p] * cost[i][j][p]).into());
            }
            let pair_lo = demand[j][p] * lo_unit;
            let pair_hi = hi_cost;
            total_lo += pair_lo;
            total_hi += pair_hi;
            let pair = m.new_int_decision(pair_lo..=pair_hi);
            let pair_expr: IntLinearExp = terms.into_iter().sum();
            m.linear(pair_expr).eq(pair).post()?;
            pair_costs.push(pair);
        }
    }

    // The total cost is the sum of the per-pair costs.
    let total = m.new_int_decision(total_lo..=total_hi);
    let total_expr: IntLinearExp = pair_costs.into_iter().map(IntLinearExp::from).sum();
    m.linear(total_expr).eq(total).post()?;

    let mut out = Out::new();
    out.put("total_cost", total);
    out.minimise(total);
    Ok(out)
}
