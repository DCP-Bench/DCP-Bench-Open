// Graceful graph: label the n nodes of a graph with m edges with distinct
// numbers from 0..m so that the edge labels |label(x) - label(y)| (one per edge
// xy) are all different.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let m = inst.int("m"); // number of edges
    let n = inst.size("n"); // number of nodes
    let graph = inst.matrix("graph"); // graph[e] = [x, y], the two ends of edge e
    let edge_count = graph.len();

    // nodes[v] is the label of node v, a number from 0 to m.
    let nodes: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, m)).collect();
    // edges[e] is the label of edge e, a number from 1 to m.
    let edges: Vec<Var> = (0..edge_count).map(|_| solver.new_bounded_integer(1, m)).collect();

    // The label of an edge is the absolute difference of the labels of its ends:
    // diff = nodes[x] - nodes[y] (signed, between -m and m), edges[e] = |diff|.
    let signed = solver.new_constraint_tag();
    let magnitude = solver.new_constraint_tag();
    for (e, ends) in graph.iter().enumerate() {
        let diff = solver.new_bounded_integer(-m, m);
        solver
            .add_constraint(pumpkin_solver::equals(
                vec![
                    nodes[ends[0] as usize].scaled(1),
                    nodes[ends[1] as usize].scaled(-1),
                    diff.scaled(-1),
                ],
                0,
                signed,
            ))
            .post();
        solver
            .add_constraint(pumpkin_solver::absolute(diff, edges[e], magnitude))
            .post();
    }

    // All edge labels are different.
    let distinct_edges = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::all_different(edges.clone(), distinct_edges))
        .post();

    // All node labels are different.
    let distinct_nodes = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::all_different(nodes.clone(), distinct_nodes))
        .post();

    let mut model = Model::new();
    model.put("nodes", nodes);
    model.put("edges", edges);
    model
}
