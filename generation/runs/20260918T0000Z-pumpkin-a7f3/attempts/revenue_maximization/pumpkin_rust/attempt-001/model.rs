// Sell the mix of packages that earns most without overbooking any leg.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let seats = inst.ints("available_seats");
    let demand = inst.ints("demand");
    let revenue = inst.ints("revenue");
    let delta = inst.matrix("delta");
    let packages = demand.len();
    let legs = seats.len();

    let ceiling = *demand.iter().max().unwrap_or(&0);
    let sell = cp.ints(packages, 0, ceiling);
    for i in 0..packages {
        cp.le(vec![t(sell[i])], demand[i]);
    }
    for j in 0..legs {
        let uses: Vec<i32> = (0..packages).map(|i| delta[i][j]).collect();
        cp.le(weighted(&uses, &sell), seats[j]);
    }

    let earned = cp.sum(weighted(&revenue, &sell));

    let mut m = Model::new();
    m.put("packages_to_sell", sell);
    m.put("max_revenue", earned);
    m.maximise(earned);
    m
}
