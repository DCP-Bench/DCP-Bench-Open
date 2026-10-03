// Contracting costs: a contractor knows what six pairs of tradesmen charge
// together; find what each man charges.
//
// The instance has no fields: the six pair totals and the 1..5300 range of a
// charge are the puzzle's own constants, mirrored from the reference.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let names = ["paper_hanger", "painter", "plumber", "electrician", "carpenter", "mason"];
    let (paper_hanger, painter, plumber, electrician, carpenter, mason) = (0, 1, 2, 3, 4, 5);
    let x: Vec<Var> = (0..names.len()).map(|_| solver.new_bounded_integer(1, 5300)).collect();

    // What each pair of men is paid together, in dollars.
    let pairs = [
        (paper_hanger, painter, 1100),
        (painter, plumber, 1700),
        (plumber, electrician, 1100),
        (electrician, carpenter, 3300),
        (carpenter, mason, 5300),
        (mason, painter, 3200),
    ];
    let paid = solver.new_constraint_tag();
    for (p, q, total) in pairs {
        solver.add_constraint(pumpkin_solver::equals(vec![x[p], x[q]], total, paid)).post();
    }

    let mut m = Model::new();
    for (i, name) in names.iter().enumerate() {
        m.put(name, x[i]);
    }
    m
}
