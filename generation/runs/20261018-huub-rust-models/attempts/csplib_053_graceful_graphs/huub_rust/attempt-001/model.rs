// CSPLib 053, graceful graphs.
// A graph with q edges (instance field m) and n nodes (instance field n) is graceful
// if its nodes get distinct labels from {0, 1, ..., q}, and each edge xy is labelled
// |f(x) - f(y)|, with all edge labels different. Output: node labels (nodes) and
// edge labels (edges).

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("n");
    let q = inst.size("m");
    let graph = inst.matrix("graph");
    let qi = q as i64;

    // Each node gets a label in {0, ..., q}.
    // The labels of the nodes are all different.
    let nodes = m.new_int_decisions(n, 0..=qi);
    m.unique(nodes.clone()).post()?;

    // Each edge xy is labelled |f(x) - f(y)|.
    // The edge labels are all different, and each lies in 1..=q.
    let edges = m.new_int_decisions(q, 1..=qi);
    for (e, uv) in graph.iter().enumerate() {
        let (u, v) = (uv[0] as usize, uv[1] as usize);
        let diff = m.new_int_decision(-qi..=qi);
        m.linear(nodes[u] - nodes[v] - diff).eq(0).post()?;
        let abs_diff = m.abs(diff).define();
        m.linear(abs_diff - edges[e]).eq(0).post()?;
    }
    m.unique(edges.clone()).post()?;

    let mut out = Out::new();
    out.put("nodes", nodes).put("edges", edges);
    Ok(out)
}
