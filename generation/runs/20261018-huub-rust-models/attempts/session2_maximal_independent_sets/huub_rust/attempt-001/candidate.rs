// Maximal independent set: find a set of nodes with no two adjacent nodes,
// such that no further node can be added. The data gives each node's adjacent
// nodes as 1-based indices. nodes[i] is true when node i+1 is in the set.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("n");
    let adj = inst.matrix("adjacency_list");
    let nodes: Vec<View<bool>> = (0..n).map(|_| m.new_bool_decision()).collect();

    // An independent set: no two adjacent nodes are both included.
    for i in 0..n {
        for &j in &adj[i] {
            let j = (j - 1) as usize;
            if j != i {
                m.linear([nodes[i], nodes[j]].iter().copied().sum::<IntLinearExp>())
                    .le(1)
                    .post()?;
            }
        }
    }

    // A maximal set: every node not in the set has a neighbour in the set.
    for i in 0..n {
        let mut lits = vec![nodes[i]];
        for &j in &adj[i] {
            lits.push(nodes[(j - 1) as usize]);
        }
        m.linear(lits.iter().copied().sum::<IntLinearExp>())
            .ge(1)
            .post()?;
    }

    let mut out = Out::new();
    out.put("nodes", nodes);
    Ok(out)
}
