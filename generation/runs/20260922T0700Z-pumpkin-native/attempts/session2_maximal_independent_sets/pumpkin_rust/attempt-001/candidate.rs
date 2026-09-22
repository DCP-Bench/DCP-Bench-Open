// An independent set that no unchosen node could be added to.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.size("n");
    let adjacency = inst.matrix("adjacency_list");

    let nodes: Vec<Lit> = (0..n).map(|_| solver.new_literal()).collect();
    for (i, neighbours) in adjacency.iter().enumerate() {
        for &neighbour in neighbours {
            let j = neighbour as usize - 1;
            if i < j {
                let tag = solver.new_constraint_tag();
                solver
                    .add_constraint(pumpkin_solver::boolean_less_than_or_equals(
                        vec![1, 1], vec![nodes[i], nodes[j]], 1, tag))
                    .post();
            }
        }
        // maximality: chosen, or next to something chosen
        let mut options = vec![nodes[i]];
        options.extend(neighbours.iter().map(|&k| nodes[k as usize - 1]));
        let tag = solver.new_constraint_tag();
        solver.add_constraint(pumpkin_solver::clause(options, tag)).post();
    }

    let mut m = Model::new();
    m.put("nodes", nodes);
    m
}
