// Hanging weights: thirteen different weights A..M from 1 to 13 hang from a
// system of bars; find the weights that make every bar balance, where the
// weights on either side of a pivot balance when multiplied by their distances
// and a hanging bar counts as one weight equal to its total.
//
// The instance has no fields: the bar geometry is the puzzle's own data,
// mirrored from the reference's balance equations.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let n = 13;
    let names = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m"];
    let x: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(1, n as i32)).collect();
    let (a, b, c, d, e, f, g, h, i, j, k, l, m) =
        (x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7], x[8], x[9], x[10], x[11], x[12]);

    // The weights are all different.
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::all_different(x.clone(), tag)).post();

    // Balance of each bar, written as left side - right side == 0.
    let balance = solver.new_constraint_tag();
    let bars: Vec<Vec<Term>> = vec![
        // A-B bar: 4A == B
        vec![a.scaled(4), b.scaled(-1)],
        // C-D bar: 5C == D
        vec![c.scaled(5), d.scaled(-1)],
        // E-F bar: 3E == 2F
        vec![e.scaled(3), f.scaled(-2)],
        // G and the C-D bar: 3G == 2(C + D)
        vec![g.scaled(3), c.scaled(-2), d.scaled(-2)],
        // J-K bar: 3(A + B) + 2J == K + 2(G + C + D)
        vec![a.scaled(3), b.scaled(3), j.scaled(2), k.scaled(-1), g.scaled(-2), c.scaled(-2), d.scaled(-2)],
        // H-I bar: 3H == 2(E + F) + 3I
        vec![h.scaled(3), e.scaled(-2), f.scaled(-2), i.scaled(-3)],
        // L-M bar: H + I + E + F == L + 4M
        vec![h.scaled(1), i.scaled(1), e.scaled(1), f.scaled(1), l.scaled(-1), m.scaled(-4)],
        // Top bar: 4(L + M + H + I + E + F) == 3(J + K + G + A + B + C + D)
        vec![
            l.scaled(4), m.scaled(4), h.scaled(4), i.scaled(4), e.scaled(4), f.scaled(4),
            j.scaled(-3), k.scaled(-3), g.scaled(-3), a.scaled(-3), b.scaled(-3), c.scaled(-3), d.scaled(-3),
        ],
    ];
    for terms in bars {
        solver.add_constraint(pumpkin_solver::equals(terms, 0, balance)).post();
    }

    let mut out = Model::new();
    for (idx, name) in names.iter().enumerate() {
        out.put(name, x[idx]);
    }
    out
}
