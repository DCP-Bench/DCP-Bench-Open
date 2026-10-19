// arch_friends: Harriet bought four pairs of shoes (ecru espadrilles, fuchsia flats,
// purple pumps, suede sandals) at four stores (Foot Farm, Heels in a Handcart,
// The Shoe Palace, Tootsies). Each shoe and each store gets its own stop number 1 to 4.

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    // Shoes: the stop at which Harriet bought each pair.
    let ecruespadrilles = m.new_int_decision(1..=4);
    let fuchsiaflats = m.new_int_decision(1..=4);
    let purplepumps = m.new_int_decision(1..=4);
    let suedesandals = m.new_int_decision(1..=4);

    // Stores: the stop at which Harriet visited each store.
    let footfarm = m.new_int_decision(1..=4);
    let heelsinahandcart = m.new_int_decision(1..=4);
    let theshoepalace = m.new_int_decision(1..=4);
    let tootsies = m.new_int_decision(1..=4);

    // Harriet bought four different shoes, at four different stops.
    m.unique(vec![ecruespadrilles, fuchsiaflats, purplepumps, suedesandals]).post()?;
    // Harriet visited four different stores, at four different stops.
    m.unique(vec![footfarm, heelsinahandcart, theshoepalace, tootsies]).post()?;

    // Harriet bought fuchsia flats at Heels in a Handcart.
    m.linear(fuchsiaflats - heelsinahandcart).eq(0).post()?;
    // The store she visited just after buying her purple pumps was not Tootsies.
    m.linear(tootsies - purplepumps).ne(1).post()?;
    // The Foot Farm was Harriet's second stop.
    m.linear(footfarm).eq(2).post()?;
    // Two stops after leaving The Shoe Palace, Harriet bought her suede sandals.
    eq2(m, suedesandals - theshoepalace, 2)?;

    let mut out = Out::new();
    out.put("ecruespadrilles", ecruespadrilles)
        .put("fuchsiaflats", fuchsiaflats)
        .put("purplepumps", purplepumps)
        .put("suedesandals", suedesandals)
        .put("footfarm", footfarm)
        .put("heelsinahandcart", heelsinahandcart)
        .put("theshoepalace", theshoepalace)
        .put("tootsies", tootsies);
    Ok(out)
}
