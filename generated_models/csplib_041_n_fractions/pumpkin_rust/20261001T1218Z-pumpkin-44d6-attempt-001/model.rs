// Fractions puzzle (CSPLib 041): find distinct non-zero digits A..I with
// A/BC + D/EF + G/HI = 1, where BC, EF and HI are two-digit numbers.
//
// The instance has no fields: the digit range 1..9 and the 1..81 range of each
// two-digit denominator (n * n) are the reference's own constants, mirrored here.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let n = 9;
    let names = ["A", "B", "C", "D", "E", "F", "G", "H", "I"];
    let x: Vec<Var> = (0..9).map(|_| solver.new_bounded_integer(1, n)).collect();
    let (a, b, c, d, e, f, g, h, i) = (x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7], x[8]);

    // The digits are all different.
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::all_different(x.clone(), tag)).post();

    // The denominators BC, EF, HI as two-digit numbers.
    let numbers = solver.new_constraint_tag();
    let two_digit = |solver: &mut Solver, tens: Var, units: Var| -> Var {
        let v = solver.new_bounded_integer(1, n * n);
        solver
            .add_constraint(pumpkin_solver::equals(
                vec![tens.scaled(10), units.scaled(1), v.scaled(-1)],
                0,
                numbers,
            ))
            .post();
        v
    };
    let d1 = two_digit(solver, b, c);
    let d2 = two_digit(solver, e, f);
    let d3 = two_digit(solver, h, i);

    // Multiplying out the denominators:
    // A * EF * HI + D * BC * HI + G * BC * EF == BC * EF * HI.
    // Each triple product is built from binary products; the bounds are those of
    // the factors (at most 81 * 81 for a pair, times 9 or 81 for a triple).
    let products = solver.new_constraint_tag();
    let product = |solver: &mut Solver, p: Var, q: Var, hi: i32| -> Var {
        let v = solver.new_bounded_integer(1, hi);
        solver.add_constraint(pumpkin_solver::times(p, q, v, products)).post();
        v
    };
    let d1d2 = product(solver, d1, d2, 81 * 81);
    let d1d3 = product(solver, d1, d3, 81 * 81);
    let d2d3 = product(solver, d2, d3, 81 * 81);
    let t1 = product(solver, a, d2d3, 9 * 81 * 81);
    let t2 = product(solver, d, d1d3, 9 * 81 * 81);
    let t3 = product(solver, g, d1d2, 9 * 81 * 81);
    let all = product(solver, d1d2, d3, 81 * 81 * 81);
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(
            vec![t1.scaled(1), t2.scaled(1), t3.scaled(1), all.scaled(-1)],
            0,
            tag,
        ))
        .post();

    let mut m = Model::new();
    for (k, name) in names.iter().enumerate() {
        m.put(name, x[k]);
    }
    m
}
