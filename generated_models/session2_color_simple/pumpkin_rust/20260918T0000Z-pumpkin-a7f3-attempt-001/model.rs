// Colour adjacent countries differently, using as few colours as possible.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let graph = inst.matrix("graph");
    // The edge list numbers the countries 1..num_nodes.
    let num_nodes = graph.iter().flatten().copied().max().unwrap_or(0) as usize;

    let colors = cp.ints(num_nodes, 1, num_nodes as i32);
    for edge in &graph {
        cp.differ(colors[edge[0] as usize - 1], colors[edge[1] as usize - 1]);
    }

    let used = cp.int(1, num_nodes as i32);
    cp.max(terms(&colors), used);

    let mut m = Model::new();
    m.put("colors", colors);
    m.minimise(used);
    m
}
