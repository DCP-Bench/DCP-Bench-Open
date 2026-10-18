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

    // Every city is visited exactly once and the tour returns to the origin city.
    let next = m.new_int_decisions(n, 0..=(n as i64 - 1));
    circuit(m, &next)?;

    // Each city leaves the tour towards exactly one other city: one indicator per
    // (origin, destination) pair, and exactly one indicator is true per origin.
    let mut leg_min = Vec::with_capacity(n);
    let mut leg_max = Vec::with_capacity(n);
    for i in 0..n {
        let mut row_bools = Vec::with_capacity(n);
        for j in 0..n {
            if j != i {
                let b = m.linear(next[i]).eq(j as i64).reify();
                row_bools.push(b);
            }
        }
        m.linear(row_bools.iter().copied().sum::<IntLinearExp>()).eq(1).post()?;
        let others: Vec<i64> = (0..n).filter(|&j| j != i).map(|j| d[i][j]).collect();
        leg_min.push(*others.iter().min().unwrap_or(&0));
        leg_max.push(*others.iter().max().unwrap_or(&0));
    }

    // Each leg costs the distance from its origin city to the next city on the tour.
    // Its domain is limited to the shortest and longest distance leaving that city.
    let mut legs = Vec::with_capacity(n);
    for i in 0..n {
        let leg = m.new_int_decision(leg_min[i]..=leg_max[i]);
        m.element(d[i].clone()).index(next[i]).result(leg).post()?;
        legs.push(leg);
    }

    // The travel distance is the sum of all legs.
    let lo: i64 = leg_min.iter().sum();
    let hi: i64 = leg_max.iter().sum();
    let total = m.new_int_decision(lo..=hi);
    m.linear(legs.iter().copied().sum::<IntLinearExp>()).eq(total).post()?;

    let mut out = Out::new();
    out.put("travel_distance", total);
    out.minimise(total);
    Ok(out)
}
