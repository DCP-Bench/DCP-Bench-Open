// Candies: Alice gives candies to children sitting in a line, each with a rating.
// Every child gets at least 1 candy. Of two immediate neighbours, the child with
// the higher rating gets more candies than the other. Minimise the total number
// of candies. Outputs: x (candies per child) and z (the total).

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let ratings = inst.ints("ratings");
    let n = ratings.len();
    let max_candies = n as i64;

    // Each child gets at least 1 candy.
    let x = m.new_int_decisions(n, 1..=max_candies);

    // If a child has a higher rating than a neighbour, that child gets more candies.
    for i in 0..n.saturating_sub(1) {
        if ratings[i] > ratings[i + 1] {
            m.linear(x[i] - x[i + 1]).ge(1).post()?;
        } else if ratings[i] < ratings[i + 1] {
            m.linear(x[i + 1] - x[i]).ge(1).post()?;
        }
    }

    // The total is the sum of all candies.
    let z = m.new_int_decision(0..=max_candies * max_candies);
    m.linear(x.iter().copied().sum::<IntLinearExp>()).eq(z).post()?;

    let mut out = Out::new();
    out.put("x", x).put("z", z);
    out.minimise(z);
    Ok(out)
}
