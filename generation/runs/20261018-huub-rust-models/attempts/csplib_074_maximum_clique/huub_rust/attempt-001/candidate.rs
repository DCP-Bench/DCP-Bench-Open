// csplib_074_maximum_clique: maximum clique in a simple undirected graph G = (V, E).
// Output c[i] is 1 if vertex i is in the clique, 0 otherwise. The clique is maximised.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("n");
    let adj = inst.matrix("adj");

    let c: Vec<View<bool>> = (0..n).map(|_| m.new_bool_decision()).collect();

    // A clique is a subset of vertices where every two distinct vertices are adjacent.
    // Two distinct vertices that are not adjacent cannot both be in the clique.
    for i in 0..n {
        for j in (i + 1)..n {
            if adj[i][j] == 0 {
                let pair: IntLinearExp = [c[i], c[j]].iter().copied().sum();
                m.linear(pair).le(1).post()?;
            }
        }
    }

    // The objective is the number of selected vertices, which is maximised.
    let total: IntLinearExp = c.iter().copied().sum();
    let obj = m.new_int_decision(0..=n as i64);
    m.linear(total).eq(obj).post()?;

    let mut out = Out::new();
    out.put("c", c);
    out.maximise(obj);
    Ok(out)
}
