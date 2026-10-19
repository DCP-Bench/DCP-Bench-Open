// Arch Friends: Harriet bought four pairs of shoes (ecru espadrilles, fuchsia flats,
// purple pumps, suede sandals) at four stores (Foot Farm, Heels in a Handcart,
// The Shoe Palace, Tootsies). Each purchase is one stop, numbered 1 to 4.
// Output: the stop number of each shoe and of each store.

fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let ecru = IntVar::new(1..=4);
    let fuchsia = IntVar::new(1..=4);
    let purple = IntVar::new(1..=4);
    let suede = IntVar::new(1..=4);
    let foot = IntVar::new(1..=4);
    let heels = IntVar::new(1..=4);
    let palace = IntVar::new(1..=4);
    let tootsies = IntVar::new(1..=4);

    // the values are integers from 1 to 4: each shoe bought at a different stop
    let shoes = vec![ecru.clone(), fuchsia.clone(), purple.clone(), suede.clone()];
    all_different(s, &shoes)?;

    // such that the same value denotes the same shoe or store: each store at a different stop
    let stores = vec![foot.clone(), heels.clone(), palace.clone(), tootsies.clone()];
    all_different(s, &stores)?;

    // Harriet bought fuchsia flats at Heels in a Handcart.
    post(s, iv(&fuchsia) - iv(&heels), Comparator::Equal, 0)?;

    // The store she visited just after buying her purple pumps was not Tootsies.
    // Pumps at the last stop have no next store, so only stops 1 to 3 give a constraint.
    for k in 1..=3i64 {
        let pumps_at_k = reify_eq(s, iv(&purple), k)?;
        let tootsies_next = reify_eq(s, iv(&tootsies), k + 1)?;
        s.add_clause([!pumps_at_k, !tootsies_next])?;
    }

    // The Foot Farm was Harriet's second stop.
    post(s, iv(&foot), Comparator::Equal, 2)?;

    // Two stops after leaving The Shoe Palace, Harriet bought her suede sandals.
    post(s, iv(&suede) - iv(&palace), Comparator::Equal, 2)?;

    let mut out = Out::new();
    out.put("ecruespadrilles", &ecru)
        .put("fuchsiaflats", &fuchsia)
        .put("purplepumps", &purple)
        .put("suedesandals", &suede)
        .put("footfarm", &foot)
        .put("heelsinahandcart", &heels)
        .put("theshoepalace", &palace)
        .put("tootsies", &tootsies);
    Ok(out)
}
