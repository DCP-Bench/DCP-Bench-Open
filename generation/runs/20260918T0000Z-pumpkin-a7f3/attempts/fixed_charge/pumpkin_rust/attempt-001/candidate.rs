// Most profit from three garments, each needing a rented machine.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let num_machines = inst.size("num_machines");
    let num_products = inst.size("num_products");
    let renting_cost = inst.ints("renting_cost");
    let capacity = inst.ints("capacity");
    let max_production = inst.int("max_production");
    // product[p] is (profit, machine); use[p][r] is the draw on resource r.
    let product = inst.matrix("product");
    let use = inst.matrix("use");
    let resources = capacity.len();

    let rent = cp.bools(num_machines);
    let produce = cp.ints(num_products, 0, max_production);

    for r in 0..resources {
        let draw: Vec<i32> = (0..num_products).map(|p| use[p][r]).collect();
        cp.le(weighted(&draw, &produce), capacity[r]);
    }
    // Nothing is produced unless its machine is rented.
    for p in 0..num_products {
        let machine = product[p][1] as usize;
        cp.le(vec![t(produce[p]), c(-max_production, rent[machine])], 0);
    }

    // 0..10000 is the bound the reference declares for the profit.
    let z = cp.int(0, 10000);
    let profit: Vec<i32> = (0..num_products).map(|p| product[p][0]).collect();
    let mut balance = weighted(&profit, &produce);
    let negated: Vec<i32> = renting_cost.iter().map(|v| -v).collect();
    balance.extend(weighted(&negated, &rent));
    cp.sum_eq(balance, z);

    let mut m = Model::new();
    m.put("z", z);
    m.maximise(z);
    m
}
