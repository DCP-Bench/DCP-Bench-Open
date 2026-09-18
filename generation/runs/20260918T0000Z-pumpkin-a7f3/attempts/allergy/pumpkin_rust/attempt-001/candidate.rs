// Match four friends to their allergy and surname.
// The clues are the puzzle, so the instance carries no fields.
fn build(_inst: &Instance, cp: &mut Cp) -> Model {
    let n = 4;
    // Friends: Debra = 0, Janet = 1, Hugh = 2, Rick = 3.
    let (debra, janet, hugh, rick) = (0, 1, 2, 3);

    // foods[i] is the friend allergic to food i; surnames[i] the friend named i.
    let foods = cp.ints(n, 0, n as i32 - 1);
    let surnames = cp.ints(n, 0, n as i32 - 1);
    cp.all_different(terms(&foods));
    cp.all_different(terms(&surnames));

    let (eggs, mold, nuts, ragweed) = (foods[0], foods[1], foods[2], foods[3]);
    let (baxter, lemon, malone, fleet) = (surnames[0], surnames[1], surnames[2], surnames[3]);

    cp.ne(vec![t(mold)], rick);
    cp.same(eggs, baxter);
    cp.ne(vec![t(lemon)], hugh);
    cp.ne(vec![t(fleet)], hugh);
    cp.eq(vec![t(ragweed)], debra);
    cp.ne(vec![t(lemon)], janet);
    cp.ne(vec![t(eggs)], janet);
    cp.ne(vec![t(mold)], janet);

    let mut m = Model::new();
    m.put("eggs", eggs);
    m.put("mold", mold);
    m.put("nuts", nuts);
    m.put("ragweed", ragweed);
    m.put("baxter", baxter);
    m.put("lemon", lemon);
    m.put("malone", malone);
    m.put("fleet", fleet);
    m
}
