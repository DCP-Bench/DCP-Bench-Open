// Fixed-charge production planning (maximise profit minus machine rent).
// A company manufactures shirts, shorts and pants. Each product requires labor
// hours and cloth from limited capacities, and each product can be manufactured
// only by renting its machine. The profit on each product excludes the rent.
// Maximise the profit.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let product = inst.matrix("product");
    let usage = inst.matrix("use");
    let capacity = inst.ints("capacity");
    let renting = inst.ints("renting_cost");
    let max_prod = inst.int("max_production");
    let np = inst.size("num_products");
    let nm = inst.size("num_machines");

    // Number of units produced of each product.
    let x: Vec<View<i64>> = (0..np).map(|_| m.new_int_decision(0..=max_prod)).collect();
    // Whether machine k is rented (1) or not (0).
    let rent: Vec<View<i64>> = (0..nm).map(|_| m.new_int_decision(0..=1)).collect();

    // A product can be manufactured only by renting its machine.
    for p in 0..np {
        let k = product[p][1] as usize;
        m.linear(x[p] - rent[k] * max_prod).le(0).post()?;
    }

    // The products together must not exceed the labor and cloth capacities.
    for (r, &cap) in capacity.iter().enumerate() {
        let used: IntLinearExp = (0..np).map(|p| x[p] * usage[p][r]).sum();
        m.linear(used).le(cap).post()?;
    }

    // Profit of the products made, minus the rent of the machines.
    let profit: IntLinearExp = (0..np).map(|p| x[p] * product[p][0]).sum();
    let rent_cost: IntLinearExp = (0..nm).map(|k| rent[k] * renting[k]).sum();
    let lo = -renting.iter().sum::<i64>();
    let hi: i64 = (0..np).map(|p| product[p][0] * max_prod).sum();
    let z = m.new_int_decision(lo..=hi);
    m.linear(profit - rent_cost).eq(z).post()?;

    let mut out = Out::new();
    out.put("z", z);
    out.maximise(z);
    Ok(out)
}
