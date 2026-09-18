// Cheapest diet meeting every nutritional minimum.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let price = inst.ints("price");
    let limits = inst.ints("limits");
    let n = inst.size("n");

    // The macro table belongs to the problem statement, not to the instance:
    // calories, chocolate, sugar and fat per serving of each of the four foods.
    let macros: [[i32; 4]; 4] = [
        [400, 200, 150, 500],
        [3, 2, 0, 0],
        [2, 2, 4, 4],
        [2, 4, 1, 5],
    ];

    // 0..10000 servings and 0..1000 cents are the bounds the reference declares.
    let x = cp.ints(n, 0, 10000);
    for (row, &least) in macros.iter().zip(&limits) {
        cp.ge(weighted(row, &x), least);
    }

    let cost = cp.int(0, 1000);
    cp.sum_eq(weighted(&price, &x), cost);

    let mut m = Model::new();
    m.put("cost", cost);
    m.minimise(cost);
    m
}
