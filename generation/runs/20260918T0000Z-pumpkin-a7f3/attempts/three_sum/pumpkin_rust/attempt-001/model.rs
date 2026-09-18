// Pick exactly m of the given integers so that they sum to zero.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let nums = inst.ints("nums");
    let m_count = inst.int("m");
    let n = nums.len();

    let indices = cp.bools(n);
    cp.eq(weighted(&nums, &indices), 0);
    cp.exactly(&indices, m_count);

    let mut m = Model::new();
    m.put("indices", indices);
    m
}
