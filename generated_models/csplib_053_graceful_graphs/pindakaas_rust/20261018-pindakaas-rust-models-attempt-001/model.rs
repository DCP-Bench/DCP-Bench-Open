// Graceful graphs (csplib 053): label the nodes of a graph with q edges by
// distinct values from {0, ..., q} so that the edge labels |f(x) - f(y)| are
// all different. Print the node labels and the edge labels.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.size("n");
    let m = inst.size("m");
    let graph = inst.matrix("graph");
    let q = m as i64;

    // Each node gets a unique label from {0, ..., q}.
    let nodes: Vec<IntVar> = (0..n).map(|_| IntVar::new(0..=q)).collect();
    all_different(s, &nodes)?;

    // The edge labels are all different.
    let edges: Vec<IntVar> = (0..m).map(|_| IntVar::new(0..=q)).collect();
    all_different(s, &edges)?;

    // Each edge is labelled with the absolute difference of its end labels.
    for (j, e) in graph.iter().enumerate() {
        let a = e[0] as usize;
        let b = e[1] as usize;
        // The edge label is the absolute difference of its end labels.
        let d = define(s, iv(&nodes[a]) - iv(&nodes[b]))?;
        abs_eq(s, &d, &edges[j])?;
    }

    let mut out = Out::new();
    out.put("nodes", &nodes).put("edges", &edges);
    Ok(out)
}
