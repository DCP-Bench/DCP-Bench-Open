// Maximal independent set: find a set of nodes of the graph such that no two
// nodes in the set are adjacent, and no node outside the set can be added.
// Output nodes[i] is true when node i+1 is in the set.

// The data provides an array containing for each node of the graph the set of
// adjacent nodes. Adjacency is 1-based in the data.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.size("n");
    let adj = inst.matrix("adjacency_list");

    // One Boolean per node: true when the node is in the set.
    let x: Vec<Lit> = (0..n).map(|_| s.new_lit()).collect();

    // An independent set: no two of its nodes are adjacent.
    // For each node i and each neighbour j of i, not both x_i and x_j.
    for i in 0..n {
        for &j in &adj[i] {
            let j = (j - 1) as usize;
            s.add_clause(vec![!x[i], !x[j]])?;
        }
    }

    // A maximal set: every node outside the set has a neighbour inside it.
    // For each node i, x_i or some neighbour of i is in the set.
    for i in 0..n {
        let mut clause = vec![x[i]];
        for &j in &adj[i] {
            clause.push(x[(j - 1) as usize]);
        }
        s.add_clause(clause)?;
    }

    let mut out = Out::new();
    out.put("nodes", &x);
    Ok(out)
}
