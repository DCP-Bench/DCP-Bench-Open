// Dinner: how many grandparents, parents and children go to dinner.
// The problem fixes its numbers in the description, so the instance carries no data.

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    // We're going out to dinner taking 1-6 grandparents, 1-10 parents and/or 1-40 children
    let grandparents = m.new_int_decision(1..=6);
    let parents = m.new_int_decision(1..=10);
    let children = m.new_int_decision(1..=40);

    // There must be 20 total people at dinner
    m.linear(grandparents + parents + children).eq(20).post()?;

    // Grandparents cost $3 for dinner, parents $2 and children $0.50, and it must cost $20.
    // Costs are in cents: 300 per grandparent, 200 per parent, 50 per child, 2000 in total.
    m.linear(grandparents * 300 + parents * 200 + children * 50)
        .eq(2000)
        .post()?;

    // Print the number of grandparents, parents and children going to dinner
    let mut out = Out::new();
    out.put("grandparents", grandparents)
        .put("parents", parents)
        .put("children", children);
    Ok(out)
}
