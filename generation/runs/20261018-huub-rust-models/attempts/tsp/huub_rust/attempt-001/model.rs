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
// Each leg costs the distance from its origin city to its destination city.
fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let loc = inst.matrix("locations");
    let n = loc.len();
    let d = distance_table(&loc);
    let max_d = d.iter().flatten().copied().max().unwrap_or(0);

    // Every city is visited exactly once and the tour returns to the origin city.
    let next = m.new_int_decisions(n, 0..=(n as i64 - 1));
    circuit(m, &next)?;

    // Each leg costs the distance from its origin city to the next city on the tour.
    let mut legs = Vec::with_capacity(n);
    for i in 0..n {
        let leg = m.new_int_decision(0..=max_d);
        m.element(d[i].clone()).index(next[i]).result(leg).post()?;
        legs.push(leg);
    }

    // The travel distance is the sum of all legs.
    let total = m.new_int_decision(0..=max_d * n as i64);
    m.linear(legs.iter().copied().sum::<IntLinearExp>()).eq(total).post()?;

    let mut out = Out::new();
    out.put("travel_distance", total);
    out.minimise(total);
    Ok(out)
}
