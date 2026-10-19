// Travelling salesman problem: visit every city exactly once and return to the
// origin city, minimising the total travel distance. The distance between two
// cities is the Euclidean distance between their points, rounded to an integer.
// Instance field: locations (one [x, y] pair per city).
// Output: travel_distance (the optimal total distance).

// Distance between every pair of cities: the Euclidean distance rounded to an integer.
fn distance_table(loc: &[Vec<i64>]) -> Vec<Vec<i64>> {
    let n = loc.len();
    let mut d = vec![vec![0i64; n]; n];
    for i in 0..n {
        for j in 0..n {
            let dx = loc[i][0] - loc[j][0];
            let dy = loc[i][1] - loc[j][1];
            d[i][j] = ((dx * dx + dy * dy) as f64).sqrt().round() as i64;
        }
    }
    d
}

// The cities form one tour: next[i] is the city visited after city i.
// The travel distance is the sum of the distances of the legs of the tour.
fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let loc = inst.matrix("locations");
    let n = loc.len();
    let d = distance_table(&loc);

    // Every city is visited exactly once and the tour returns to the origin city.
    let next = m.new_int_decisions(n, 0..=(n as i64 - 1));
    circuit(m, &next)?;

    // Leg indicators: uses[i][j] holds when the tour goes from city i to city j.
    // Each city leaves the tour towards exactly one other city.
    let mut uses: Vec<Vec<View<bool>>> = vec![Vec::new(); n];
    for i in 0..n {
        for j in 0..n {
            if j != i {
                uses[i].push(m.linear(next[i]).eq(j as i64).reify());
            }
        }
        let row: Vec<View<bool>> = uses[i].clone();
        m.linear(row.iter().copied().sum::<IntLinearExp>()).eq(1).post()?;
    }

    // The travel distance is the sum of the distances of the legs taken.
    let mut legs = IntLinearExp::from(0i64);
    let mut hi: i64 = 0;
    for i in 0..n {
        let mut best = 0i64;
        let mut k = 0usize;
        for j in 0..n {
            if j != i {
                let w = d[i][j];
                legs = legs + uses[i][k] * w;
                best = best.max(w);
                k += 1;
            }
        }
        hi += best;
    }
    let total = m.new_int_decision(0..=hi);
    m.linear(legs).eq(total).post()?;

    let mut out = Out::new();
    out.put("travel_distance", total);
    out.minimise(total);
    Ok(out)
}
