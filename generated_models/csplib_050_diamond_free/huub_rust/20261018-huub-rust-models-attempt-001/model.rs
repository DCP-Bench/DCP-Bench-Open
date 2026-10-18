// csplib_050_diamond_free: degree sequences of simple diamond-free graphs on N vertices.
// The output is the adjacency matrix of a witness graph whose degree sequence is
// non-increasing, has every degree positive and divisible by 3, and has a degree sum
// divisible by 12. A diamond is four vertices with at least five edges between them.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("N");

    // A Boolean fixed to false, used on the diagonal: a graph has no loop edges.
    // The indicator of the false equation 0 = 1 is a false view.
    let zero = m.linear(IntLinearExp::from(0i64)).eq(1).reify();

    // The graph is simple and undirected: one Boolean per unordered pair u < v,
    // mirrored into both matrix cells.
    let mut adj: Vec<Vec<View<bool>>> = vec![vec![zero; n]; n];
    for u in 0..n {
        for v in (u + 1)..n {
            let e = m.new_bool_decision();
            adj[u][v] = e;
            adj[v][u] = e;
        }
    }

    // Each vertex has a degree d_v that is at least 1, divisible by 3, and at most n - 1.
    // The degree is written as 3 * q with q >= 1.
    let qmax = ((n - 1) / 3) as i64;
    let mut deg: Vec<View<i64>> = Vec::new();
    for _u in 0..n {
        let d = m.new_int_decision(0..=(n as i64 - 1));
        let q = m.new_int_decision(1..=qmax);
        m.linear(q * 3 - d).le(0).post()?;
        m.linear(q * 3 - d).ge(0).post()?;
        deg.push(d);
    }

    // The degree of each vertex is the number of its incident edges (no loops).
    for u in 0..n {
        let row: Vec<View<bool>> = (0..n).filter(|&v| v != u).map(|v| adj[u][v]).collect();
        let s: IntLinearExp = row.iter().copied().sum();
        m.linear(s).eq(deg[u]).post()?;
    }

    // The degree sequence is non-increasing: d_i >= d_{i+1}.
    for u in 0..(n - 1) {
        m.linear(deg[u + 1] - deg[u]).le(0).post()?;
    }

    // The sum of the degrees is divisible by 12. The sum of the degrees is twice the number
    // of edges, so the number of edges E must be divisible by 6: E = 6 * t.
    let max_e = (n * (n - 1) / 2) as i64;
    let mut edges: Vec<View<bool>> = Vec::new();
    for u in 0..n {
        for v in (u + 1)..n {
            edges.push(adj[u][v]);
        }
    }
    let e_total = m.new_int_decision(0..=max_e);
    let all: IntLinearExp = edges.iter().copied().sum();
    m.linear(all).eq(e_total).post()?;
    let t = m.new_int_decision(0..=(max_e / 6));
    m.linear(t * 6 - e_total).le(0).post()?;
    m.linear(t * 6 - e_total).ge(0).post()?;

    // A graph is diamond-free: for every set of four vertices, at most four edges lie
    // between them.
    for a in 0..n {
        for b in (a + 1)..n {
            for c in (b + 1)..n {
                for d in (c + 1)..n {
                    let quad: IntLinearExp = [
                        adj[a][b],
                        adj[a][c],
                        adj[a][d],
                        adj[b][c],
                        adj[b][d],
                        adj[c][d],
                    ]
                    .iter()
                    .copied()
                    .sum();
                    m.linear(quad).le(4).post()?;
                }
            }
        }
    }

    let mut out = Out::new();
    out.put("matrix", adj);
    Ok(out)
}
