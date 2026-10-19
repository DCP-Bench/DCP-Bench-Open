// Warehouse location (CSPLib 034): decide which warehouses to open, and supply each store
// from one open warehouse within the warehouse capacities, minimising the total cost of
// maintenance for the open warehouses plus the supply cost of every store.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let w_count = inst.size("n_suppliers");
    let s_count = inst.size("n_stores");
    let building = inst.int("building_cost");
    let capacity = inst.ints("capacity");
    let cost = inst.matrix("cost_matrix");

    let mut max_cost = 0i64;
    for row in &cost {
        for &c in row {
            max_cost = max_cost.max(c);
        }
    }

    // Each warehouse is either open or closed.
    let open: Vec<View<bool>> = (0..w_count).map(|_| m.new_bool_decision()).collect();

    // Each store is supplied by exactly one warehouse, numbered 0 to n_suppliers-1.
    let assign: Vec<View<i64>> = (0..s_count)
        .map(|_| m.new_int_decision(0..=(w_count as i64) - 1))
        .collect();

    // Indicators: store s is supplied by warehouse w, and the negation of that.
    let mut eq: Vec<Vec<View<bool>>> = Vec::with_capacity(s_count);
    for s in 0..s_count {
        let mut row = Vec::with_capacity(w_count);
        for w in 0..w_count {
            row.push(m.linear(assign[s]).eq(w as i64).reify());
        }
        eq.push(row);
    }

    // Each store must be supplied by an open warehouse: a store assigned to warehouse w
    // requires that warehouse to be open.
    for s in 0..s_count {
        for w in 0..w_count {
            let not_w = m.linear(assign[s]).ne(w as i64).reify();
            m.proposition(BoolFormula::Atom(open[w]) | BoolFormula::Atom(not_w))
                .post()?;
        }
    }

    // Capacity: the stores supplied by a warehouse do not exceed its capacity.
    for w in 0..w_count {
        let load = (0..s_count).map(|s| eq[s][w]).sum::<IntLinearExp>();
        m.linear(load).le(capacity[w]).post()?;
    }

    // Supply cost of each store: the entry of its row for the warehouse it is assigned to.
    let supply: Vec<View<i64>> = (0..s_count)
        .map(|s| m.element(cost[s].clone()).index(assign[s]).define())
        .collect();
    let supply_sum = m.new_int_decision(0..=max_cost * s_count as i64);
    m.linear(supply.iter().copied().sum::<IntLinearExp>())
        .eq(supply_sum)
        .post()?;

    // Maintenance cost: the building cost for each open warehouse.
    let n_open = m.new_int_decision(0..=w_count as i64);
    m.linear(open.iter().copied().sum::<IntLinearExp>())
        .eq(n_open)
        .post()?;

    // Total cost: the maintenance cost plus the supply cost.
    let upper = max_cost * s_count as i64 + building * w_count as i64;
    let total = m.new_int_decision(0..=upper);
    m.linear(supply_sum + n_open * building).eq(total).post()?;

    let mut out = Out::new();
    out.put("open_warehouses", open)
        .put("supplier_assignment", assign)
        .put("total_cost", total);
    out.minimise(total);
    Ok(out)
}
