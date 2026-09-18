// Largest set of mutually adjacent vertices.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let n = inst.size("n");
    let adj = inst.matrix("adj");

    let chosen = cp.bools(n);
    for i in 0..n {
        for j in (i + 1)..n {
            if adj[i][j] == 0 {
                cp.at_most(&[chosen[i], chosen[j]], 1);
            }
        }
    }

    let size = cp.int(0, n as i32);
    let ones = vec![1; n];
    cp.bool_sum_eq(&ones, &chosen, size);

    let mut m = Model::new();
    m.put("c", chosen);
    m.maximise(size);
    m
}
