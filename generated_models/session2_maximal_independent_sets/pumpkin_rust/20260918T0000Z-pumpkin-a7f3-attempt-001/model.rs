// An independent set that no unchosen node could be added to.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let n = inst.size("n");
    let adjacency = inst.matrix("adjacency_list");

    let nodes = cp.bools(n);
    for (i, neighbours) in adjacency.iter().enumerate() {
        for &neighbour in neighbours {
            let j = neighbour as usize - 1;
            if i < j {
                cp.at_most(&[nodes[i], nodes[j]], 1);
            }
        }
        // maximality: chosen, or next to something chosen
        let mut options = vec![nodes[i]];
        options.extend(neighbours.iter().map(|&k| nodes[k as usize - 1]));
        cp.any(options);
    }

    let mut m = Model::new();
    m.put("nodes", nodes);
    m
}
