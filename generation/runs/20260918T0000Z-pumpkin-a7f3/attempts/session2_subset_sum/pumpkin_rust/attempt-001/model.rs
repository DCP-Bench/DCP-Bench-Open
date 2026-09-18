// How many bags of each coin type were stolen, given the total coins lost.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let coin_numbers = inst.ints("coin_numbers");
    let total = inst.int("total_coins_lost");

    let bags = cp.ints(coin_numbers.len(), 0, total);
    cp.eq(weighted(&coin_numbers, &bags), total);

    let mut m = Model::new();
    m.put("bags", bags);
    m
}
