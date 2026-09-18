// Knock over the dummies whose numbers add up to exactly the target.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let values = inst.ints("values");
    let target = inst.int("target_sum");

    let dummies = cp.bools(values.len());
    cp.eq(weighted(&values, &dummies), target);

    let mut m = Model::new();
    m.put("dummies", dummies);
    m
}
