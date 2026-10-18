// Diet problem: choose how many units of four foods to buy so that the total of
// each nutrition type reaches its minimum, at the lowest total cost.
// Foods (rows): chocolate cake, chocolate ice cream, cola, pineapple cheesecake.
// Nutrition types (columns): calories, chocolate (ounces), sugar (ounces), fat (ounces).
const NUT: [[i64; 4]; 4] = [[400, 3, 2, 2], [200, 2, 2, 4], [150, 0, 4, 1], [500, 0, 4, 5]];

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let price = inst.ints("price");
    let limits = inst.ints("limits");

    // Units of each food. A food never needs more units than one nutrition type
    // alone would require: the bound comes from the data and the table above.
    let mut ubs = Vec::new();
    for i in 0..4 {
        let mut ub: i64 = 0;
        for j in 0..4 {
            if NUT[i][j] > 0 {
                ub = ub.max((limits[j] + NUT[i][j] - 1) / NUT[i][j]);
            }
        }
        ubs.push(ub);
    }
    let x: Vec<View<i64>> = (0..4).map(|i| m.new_int_decision(0..=ubs[i])).collect();

    // Given the prices and the nutritional requirements (at least) for each nutrition type,
    // the diet must reach at least the required amount of each nutrition type.
    for j in 0..4 {
        m.linear(x[0] * NUT[0][j] + x[1] * NUT[1][j] + x[2] * NUT[2][j] + x[3] * NUT[3][j])
            .ge(limits[j])
            .post()?;
    }

    // The optimal diet is to minimize the cost of the products.
    let cmax: i64 = (0..4).map(|i| price[i] * ubs[i]).sum();
    let cost = m.new_int_decision(0..=cmax);
    m.linear(x[0] * price[0] + x[1] * price[1] + x[2] * price[2] + x[3] * price[3])
        .eq(cost)
        .post()?;

    let mut out = Out::new();
    out.put("cost", cost);
    out.minimise(cost);
    Ok(out)
}
