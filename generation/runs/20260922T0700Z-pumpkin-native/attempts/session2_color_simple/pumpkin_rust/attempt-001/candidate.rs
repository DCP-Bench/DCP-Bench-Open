// Colour adjacent countries differently, using as few colours as possible.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let graph = inst.matrix("graph");
    // The edge list numbers the countries 1..num_nodes.
    let num_nodes = graph.iter().flatten().copied().max().unwrap_or(0) as usize;

    let colors: Vec<Var> = (0..num_nodes)
        .map(|_| solver.new_bounded_integer(1, num_nodes as i32))
        .collect();
    for edge in &graph {
        let left = colors[edge[0] as usize - 1];
        let right = colors[edge[1] as usize - 1];
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::not_equals(
                vec![left.scaled(1), right.scaled(-1)], 0, tag))
            .post();
    }

    let used = solver.new_bounded_integer(1, num_nodes as i32);
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::maximum(colors.clone(), used.scaled(1), tag))
        .post();

    let mut m = Model::new();
    m.put("colors", colors);
    m.minimise(used);
    m
}
