// Fewest items from whole packs that still meet the target.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let packs = inst.ints("packs");
    let target = inst.int("target");
    let n = packs.len();

    // The reference allows up to twice the target of each pack size.
    let ceiling = target * 2;
    let counts: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, ceiling)).collect();
    let total = solver.new_bounded_integer(0, ceiling * n as i32);
    let mut supplied: Vec<Term> = (0..n)
        .filter(|&i| packs[i] != 0)
        .map(|i| counts[i].scaled(packs[i]))
        .collect();
    supplied.push(total.scaled(-1));
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::equals(supplied, 0, tag)).post();
    // total >= target, as an upper bound on the negation.
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::less_than_or_equals(
            vec![total.scaled(-1)], -target, tag))
        .post();

    let mut m = Model::new();
    m.put("counts", counts);
    m.minimise(total);
    m
}
