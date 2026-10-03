// Circling the squares (Dudeney): place ten different numbers A..K round a circle
// so that for any two adjacent numbers the sum of their squares equals the sum of
// the squares of the two numbers diametrically opposite them. A=16, B=2, F=8 and
// G=14 are given.
//
// The instance has no fields: the four given numbers and the range 1..99 ("no
// number need contain more than two figures") are the puzzle's own constants,
// mirrored from the reference.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let n = 10;
    let names = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "K"];
    let x: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(1, 99)).collect();
    let (a, b, f, g) = (x[0], x[1], x[5], x[6]);

    // Every square holds a different number.
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::all_different(x.clone(), tag)).post();

    // The four numbers placed as examples stand as they are.
    let given = solver.new_constraint_tag();
    for (v, value) in [(a, 16), (b, 2), (f, 8), (g, 14)] {
        solver.add_constraint(pumpkin_solver::equals(vec![v], value, given)).post();
    }

    // sq[j] is the square of x[j], at most 99 * 99.
    let squares = solver.new_constraint_tag();
    let sq: Vec<Var> = x
        .iter()
        .map(|&v| {
            let s = solver.new_bounded_integer(1, 99 * 99);
            solver.add_constraint(pumpkin_solver::times(v, v, s, squares)).post();
            s
        })
        .collect();

    // Adjacent pair and opposite pair have equal sums of squares, by position
    // (A=0 .. K=9): A,B ~ F,G; B,C ~ G,H; C,D ~ H,I; D,E ~ I,K; E,F ~ K,A.
    let opposite = solver.new_constraint_tag();
    for (x1, x2, y1, y2) in [(0, 1, 5, 6), (1, 2, 6, 7), (2, 3, 7, 8), (3, 4, 8, 9), (4, 5, 9, 0)] {
        solver
            .add_constraint(pumpkin_solver::equals(
                vec![sq[x1].scaled(1), sq[x2].scaled(1), sq[y1].scaled(-1), sq[y2].scaled(-1)],
                0,
                opposite,
            ))
            .post();
    }

    let mut m = Model::new();
    for (j, name) in names.iter().enumerate() {
        m.put(name, x[j]);
    }
    m
}
