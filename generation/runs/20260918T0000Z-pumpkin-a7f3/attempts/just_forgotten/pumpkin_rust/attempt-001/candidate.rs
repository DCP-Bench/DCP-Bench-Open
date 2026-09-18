// A permutation of the digits agreeing with each guess in exactly k places.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let sets = inst.matrix("sets");
    let correct = inst.int("num_correct_digits");
    let n = sets[0].len();

    let x = cp.ints(n, 0, n as i32 - 1);
    cp.all_different(terms(&x));
    for guess in &sets {
        let hits: Vec<Lit> = (0..n).map(|i| cp.is(x[i], guess[i])).collect();
        cp.exactly(&hits, correct);
    }

    let mut m = Model::new();
    m.put("x", x);
    m
}
