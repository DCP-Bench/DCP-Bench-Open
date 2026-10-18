// Travelling salesman problem: find the shortest tour through all cities.
// Each city is visited exactly once and the tour returns to the origin city.
// The distance between two cities is the Euclidean distance between their points, rounded to an integer.
// Minimise the optimal travel distance (travel_distance).

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let loc = inst.matrix("locations");
    let n = loc.len();
    let nn = n as i64;

    // The distance between two cities is the Euclidean distance between their points, rounded to an integer.
    let mut d = vec![vec![0i64; n]; n];
    for i in 0..n {
        for j in 0..n {
            let dx = loc[i][0] - loc[j][0];
            let dy = loc[i][1] - loc[j][1];
            d[i][j] = ((dx * dx + dy * dy) as f64).sqrt().round() as i64;
        }
    }
    let longest = d.iter().flatten().copied().max().unwrap_or(0);

    // Each city is visited exactly once: successor and predecessor of every city are distinct cities.
    let succ = m.new_int_decisions(n, 0..=(nn - 1));
    let pred = m.new_int_decisions(n, 0..=(nn - 1));
    for i in 0..n {
        m.linear(succ[i]).ne(i as i64).post()?;
        m.linear(pred[i]).ne(i as i64).post()?;
    }
    m.unique(succ.clone()).post()?;
    m.unique(pred.clone()).post()?;

    // The tour returns to the origin city and visits each city exactly once: the arcs are the same seen from both ends.
    for i in 0..n {
        for j in 0..n {
            if i == j {
                continue;
            }
            let a = succ[i].eq(j as i64);
            m.linear(pred[j]).eq(i as i64).reified_by(a).post()?;
        }
    }

    // The tour is a single cycle through all cities, starting from the origin city 0 (rank order along the tour).
    let rank = m.new_int_decisions(n, 0..=(nn - 1));
    m.linear(rank[0]).eq(0).post()?;
    for i in 0..n {
        for j in 1..n {
            if i == j {
                continue;
            }
            let a = succ[i].eq(j as i64);
            m.linear(rank[j] - rank[i]).le(1).implied_by(a).post()?;
            m.linear(rank[j] - rank[i]).ge(1).implied_by(a).post()?;
        }
    }

    // The travel distance is the sum of the distances of the legs leaving each city, and of the legs entering each city.
    let mut outl = Vec::new();
    let mut inl = Vec::new();
    for i in 0..n {
        let row: Vec<i64> = (0..n).map(|j| d[i][j]).collect();
        let col: Vec<i64> = (0..n).map(|j| d[j][i]).collect();
        let lo_o = (0..n).filter(|&j| j != i).map(|j| d[i][j]).min().unwrap_or(0);
        let lo_i = (0..n).filter(|&j| j != i).map(|j| d[j][i]).min().unwrap_or(0);
        let o = m.new_int_decision(lo_o..=longest);
        let e = m.new_int_decision(lo_i..=longest);
        m.element(row).index(succ[i]).result(o).post()?;
        m.element(col).index(pred[i]).result(e).post()?;
        outl.push(o);
        inl.push(e);
    }
    let total = m.new_int_decision(0..=longest * nn);
    m.linear(outl.iter().copied().sum::<IntLinearExp>() - total).eq(0).post()?;
    m.linear(inl.iter().copied().sum::<IntLinearExp>() - total).eq(0).post()?;

    // Each city has one leg in and one leg out, so the two cheapest distances from a city bound its legs.
    if n >= 3 {
        let mut both = IntLinearExp::from(0i64);
        for i in 0..n {
            let mut others: Vec<i64> = (0..n).filter(|&j| j != i).map(|j| d[i][j]).collect();
            others.sort();
            m.linear(outl[i] + inl[i]).ge(others[0] + others[1]).post()?;
            both = both + outl[i] + inl[i];
        }
        m.linear(both - total * 2).eq(0).post()?;
    }

    // The route visits each city exactly once, so no two cities form a short cycle of legs between them (implied cuts).
    if n > 2 {
        for i in 0..n {
            for j in (i + 1)..n {
                let s = [succ[i].eq(j as i64), succ[j].eq(i as i64)];
                m.linear(s.iter().copied().sum::<IntLinearExp>()).le(1).post()?;
            }
        }
    }
    if n > 3 {
        for i in 0..n {
            for j in 0..n {
                for k in 0..n {
                    if i == j || j == k || i == k || i > j || i > k {
                        continue;
                    }
                    let s = [succ[i].eq(j as i64), succ[j].eq(k as i64), succ[k].eq(i as i64)];
                    m.linear(s.iter().copied().sum::<IntLinearExp>()).le(2).post()?;
                }
            }
        }
    }

    let mut out = Out::new();
    out.put("travel_distance", total);
    out.minimise(total);
    Ok(out)
}
