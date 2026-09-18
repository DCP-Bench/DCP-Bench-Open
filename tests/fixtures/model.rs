fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let n = inst.int("n");
    let x = cp.int(0, n);
    let y = cp.int(0, n);
    let mut m = Model::new();
    m.put("x", x);
    m.put("y", y);
    if inst.flag("optimize") {
        cp.ge(vec![t(x), t(y)], n);
        let total = cp.sum(vec![t(x), t(y)]);
        m.minimise(total);
    } else {
        cp.eq(vec![t(x), t(y)], n);
    }
    m
}
