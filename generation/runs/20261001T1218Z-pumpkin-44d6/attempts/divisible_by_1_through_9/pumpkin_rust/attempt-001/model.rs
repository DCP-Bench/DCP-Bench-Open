// Divisible by 1 through 10: a ten-digit number using each digit 0..9 once, whose
// first k digits form a number divisible by k for every k = 1..10.
//
// The instance has no fields: the ten digits are the puzzle's own constants.
// Pumpkin integers are 32-bit, so the full ten-digit number can only be given
// the domain 0..i32::MAX here; prefixes of up to nine digits fit.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let len = 10;
    let x: Vec<Var> = (0..len).map(|_| solver.new_bounded_integer(0, 9)).collect();

    // Each digit 0..9 is used exactly once.
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::all_different(x.clone(), tag)).post();

    // t[i]: the number formed by the first i+1 digits, t[i] = 10 * t[i-1] + x[i].
    let prefix = solver.new_constraint_tag();
    let mut t: Vec<Var> = vec![x[0]];
    for i in 1..len {
        let hi = if i < 9 { 10i32.pow(i as u32 + 1) - 1 } else { i32::MAX };
        let v = solver.new_bounded_integer(0, hi);
        solver
            .add_constraint(pumpkin_solver::equals(
                vec![v.scaled(1), t[i - 1].scaled(-10), x[i].scaled(-1)],
                0,
                prefix,
            ))
            .post();
        t.push(v);
    }

    // The number formed by the first i+1 digits is divisible by i+1:
    // t[i] == (i+1) * q for some integer q.
    let divisible = solver.new_constraint_tag();
    for i in 1..len {
        let k = i as i32 + 1;
        let hi = if i < 9 { 10i32.pow(i as u32 + 1) / k } else { i32::MAX / k };
        let q = solver.new_bounded_integer(0, hi);
        solver
            .add_constraint(pumpkin_solver::equals(vec![t[i].scaled(1), q.scaled(-k)], 0, divisible))
            .post();
    }

    let mut m = Model::new();
    m.put("number", t[len - 1]);
    m
}
