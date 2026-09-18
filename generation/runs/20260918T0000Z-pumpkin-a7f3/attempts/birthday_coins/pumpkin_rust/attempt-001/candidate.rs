// Fifteen old British coins worth one pound five shillings and sixpence.
// The currency and the totals are the puzzle, so the instance carries no fields.
fn build(_inst: &Instance, cp: &mut Cp) -> Model {
    // half-crown, shilling, sixpence, in pence
    let values = [30, 12, 6];
    let total_value = 240 + 5 * 12 + 6;
    let total_coins = 15;

    let coins = cp.ints(values.len(), 0, total_coins);
    cp.eq(weighted(&values, &coins), total_value);
    cp.eq(terms(&coins), total_coins);

    let mut m = Model::new();
    m.put("half_crowns", coins[0]);
    m
}
