// Match four pairs of shoes to the four stops they were bought at.
// The clues are the puzzle, so the instance carries no fields.
fn build(_inst: &Instance, cp: &mut Cp) -> Model {
    let n = 4;
    let shoes = cp.ints(n, 1, n as i32);
    let store = cp.ints(n, 1, n as i32);
    cp.all_different(terms(&shoes));
    cp.all_different(terms(&store));

    let (ecru, fuchsia, purple, suede) = (shoes[0], shoes[1], shoes[2], shoes[3]);
    let (footfarm, heels, palace, tootsies) = (store[0], store[1], store[2], store[3]);

    // 1. fuchsia flats came from Heels in a Handcart
    cp.same(fuchsia, heels);
    // 2. the stop after the purple pumps was not Tootsies
    cp.ne(vec![t(purple), c(-1, tootsies)], -1);
    // 3. the Foot Farm was the second stop
    cp.eq(vec![t(footfarm)], 2);
    // 4. the suede sandals came two stops after The Shoe Palace
    cp.eq(vec![t(palace), c(-1, suede)], -2);

    let mut m = Model::new();
    m.put("ecruespadrilles", ecru);
    m.put("fuchsiaflats", fuchsia);
    m.put("purplepumps", purple);
    m.put("suedesandals", suede);
    m.put("footfarm", footfarm);
    m.put("heelsinahandcart", heels);
    m.put("theshoepalace", palace);
    m.put("tootsies", tootsies);
    m
}
