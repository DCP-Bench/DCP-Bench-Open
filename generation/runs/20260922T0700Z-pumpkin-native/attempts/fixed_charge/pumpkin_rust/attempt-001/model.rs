// Most profit from three garments, each needing a rented machine.
//
// The instance also names index constants -- `shirt`, `shorts`, `pants`,
// `shirtM`, `shortM`, `pantM`, and the lists `products`, `machines` and
// `resources`. The reference uses them only to enumerate, as `for p in
// products`, and each list is exactly `0..len - 1`; the loops below enumerate
// the same ranges directly. `product[p][1]`, the machine a product needs, is
// likewise unused by the reference: it caps production with `rent[p]`, indexing
// by the product rather than by its machine. The two agree on the listed
// instance, and the reference is the specification, so `rent[p]` is what this
// model posts.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let num_machines = inst.size("num_machines");
    let num_products = inst.size("num_products");
    let renting_cost = inst.ints("renting_cost");
    let capacity = inst.ints("capacity");
    let max_production = inst.int("max_production");
    // product[p] is (profit, machine); usage[p][r] is the draw on resource r.
    let product = inst.matrix("product");
    let usage = inst.matrix("use");
    let resources = capacity.len();

    let rent: Vec<Lit> = (0..num_machines).map(|_| solver.new_literal()).collect();
    let produce: Vec<Var> = (0..num_products)
        .map(|_| solver.new_bounded_integer(0, max_production))
        .collect();

    for r in 0..resources {
        // A product that draws nothing on this resource carries coefficient
        // zero, which Pumpkin cannot scale by.
        let draw: Vec<Term> = (0..num_products)
            .filter(|&p| usage[p][r] != 0)
            .map(|p| produce[p].scaled(usage[p][r]))
            .collect();
        if draw.is_empty() {
            continue;
        }
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::less_than_or_equals(draw, capacity[r], tag))
            .post();
    }
    // Nothing is produced unless its machine is rented.
    for p in 0..num_products {
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::less_than_or_equals(
                vec![
                    produce[p].scaled(1),
                    rent[p].get_integer_variable().scaled(-max_production),
                ],
                0,
                tag,
            ))
            .post();
    }

    // 0..10000 is the bound the reference declares for the profit.
    let z = solver.new_bounded_integer(0, 10000);
    let mut balance: Vec<Term> = (0..num_products)
        .filter(|&p| product[p][0] != 0)
        .map(|p| produce[p].scaled(product[p][0]))
        .collect();
    balance.extend(
        (0..num_machines)
            .filter(|&k| renting_cost[k] != 0)
            .map(|k| rent[k].get_integer_variable().scaled(-renting_cost[k])),
    );
    balance.push(z.scaled(-1));
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::equals(balance, 0, tag)).post();

    let mut m = Model::new();
    m.put("z", z);
    m.maximise(z);
    m
}
