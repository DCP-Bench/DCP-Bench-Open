// csplib_050_diamond_free: a simple undirected graph on N vertices whose degree
// sequence has every degree > 0 and divisible by 3, with the degree sum divisible
// by 12, and which has no diamond (a set of four vertices with at least five edges
// among them). Output the adjacency matrix as booleans.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.size("N");

    // One Boolean per unordered pair {i, j}, i < j. The matrix is symmetric and the
    // diagonal is false (no loop edges).
    let mut edge = vec![vec![None::<Lit>; n]; n];
    for i in 0..n {
        for j in (i + 1)..n {
            let l = s.new_lit();
            edge[i][j] = Some(l.clone());
            edge[j][i] = Some(l);
        }
    }
    let lit = |i: usize, j: usize| edge[i][j].clone().expect("off-diagonal edge");

    // The degree of each vertex is a multiple of 3 and greater than zero:
    // deg_i = 3 * t_i with 1 <= t_i <= (n - 1) / 3, since no degree exceeds n - 1.
    let t_max = ((n - 1) / 3) as i64;
    let mut t: Vec<IntVar> = Vec::with_capacity(n);
    for i in 0..n {
        let ti = IntVar::new(1..=t_max);
        let mut deg = LinExp::default();
        for j in 0..n {
            if j != i {
                deg += LinExp::from(lit(i, j));
            }
        }
        // The degree of vertex i is the number of its incident edges.
        post(s, deg - scaled(&ti, 3), Comparator::Equal, 0)?;
        t.push(ti);
    }

    // The degrees are in non-increasing order: d_i >= d_{i+1}.
    for i in 0..n.saturating_sub(1) {
        post(s, iv(&t[i + 1]) - iv(&t[i]), Comparator::LessEq, 0)?;
    }

    // The sum of the degrees is a multiple of 12, so the number of edges is a
    // multiple of 6: sum of all edges = 6 * m.
    let n_pairs = (n * (n - 1) / 2) as i64;
    let m = IntVar::new(0..=(n_pairs / 6));
    let mut all_edges = LinExp::default();
    for i in 0..n {
        for j in (i + 1)..n {
            all_edges += LinExp::from(lit(i, j));
        }
    }
    post(s, all_edges - scaled(&m, 6), Comparator::Equal, 0)?;

    // The graph is diamond-free: every set of four vertices has at most four edges
    // among them (no induced subgraph with at least five edges).
    for a in 0..n {
        for b in (a + 1)..n {
            for c in (b + 1)..n {
                for d in (c + 1)..n {
                    let vs = [a, b, c, d];
                    let mut e = LinExp::default();
                    for p in 0..4 {
                        for q in (p + 1)..4 {
                            e += LinExp::from(lit(vs[p], vs[q]));
                        }
                    }
                    post(s, e, Comparator::LessEq, 4)?;
                }
            }
        }
    }

    // Output the adjacency matrix: diagonal false, off-diagonal the edge literal.
    let mut matrix: Vec<Vec<BoolVal>> = Vec::with_capacity(n);
    for i in 0..n {
        let mut row: Vec<BoolVal> = Vec::with_capacity(n);
        for j in 0..n {
            if i == j {
                row.push(BoolVal::Const(false));
            } else {
                row.push(BoolVal::Lit(lit(i, j)));
            }
        }
        matrix.push(row);
    }
    let mut out = Out::new();
    out.put("matrix", &matrix);
    Ok(out)
}
