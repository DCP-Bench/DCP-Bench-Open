// De Bruijn sequence: a cyclic sequence of base^n digits (each from 0 to
// base - 1) in which every possible string of n digits occurs exactly once as
// a run of n consecutive digits, going round the end of the sequence.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let base = inst.int("base"); // size of the alphabet
    let n = inst.size("n"); // order: length of the strings
    let m = (base as usize).pow(n as u32); // length of the sequence, base^n

    // de_bruijn[i] is the digit at position i of the sequence.
    let de_bruijn: Vec<Var> = (0..m).map(|_| solver.new_bounded_integer(0, base - 1)).collect();

    // x[i] is the number written by the n digits that start at position i
    // (position m - 1 is followed by position 0), reading them as a number in
    // the given base with the first digit most significant. There are base^n
    // such numbers, 0 .. base^n - 1.
    let x: Vec<Var> = (0..m).map(|_| solver.new_bounded_integer(0, m as i32 - 1)).collect();
    let window = solver.new_constraint_tag();
    for i in 0..m {
        let mut terms: Vec<Term> = vec![x[i].scaled(-1)];
        for j in 0..n {
            let weight = base.pow((n - 1 - j) as u32);
            terms.push(de_bruijn[(i + j) % m].scaled(weight));
        }
        solver
            .add_constraint(pumpkin_solver::equals(terms, 0, window))
            .post();
    }

    // Every string occurs exactly once: the numbers read at the m starting
    // positions are all different, so all base^n strings appear.
    let each_once = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::all_different(x, each_once))
        .post();

    let mut model = Model::new();
    model.put("de_bruijn", de_bruijn);
    model
}
