// Sums of two squares in two ways: four different numbers a, b, c, d in 1..100
// with a^2 + b^2 == c^2 + d^2.
//
// The instance has no fields: the range 1..100 is the puzzle's own constant,
// mirrored from the reference.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let (lo, hi) = (1, 100);
    let x: Vec<Var> = (0..4).map(|_| solver.new_bounded_integer(lo, hi)).collect();

    // sq[k] is the square of x[k], between lo^2 and hi^2.
    let squares = solver.new_constraint_tag();
    let sq: Vec<Var> = x
        .iter()
        .map(|&v| {
            let s = solver.new_bounded_integer(lo * lo, hi * hi);
            solver.add_constraint(pumpkin_solver::times(v, v, s, squares)).post();
            s
        })
        .collect();

    // The squares of the first two numbers add up to the squares of the other two.
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(
            vec![sq[0].scaled(1), sq[1].scaled(1), sq[2].scaled(-1), sq[3].scaled(-1)],
            0,
            tag,
        ))
        .post();

    // The four numbers are different.
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::all_different(x.clone(), tag)).post();

    let mut m = Model::new();
    m.put("a", x[0]);
    m.put("b", x[1]);
    m.put("c", x[2]);
    m.put("d", x[3]);
    m
}
