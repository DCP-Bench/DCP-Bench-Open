// Cheapest diet meeting every nutritional minimum.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let price = inst.ints("price");
    let limits = inst.ints("limits");
    let n = inst.size("n");

    // The macro table belongs to the problem statement, not to the instance:
    // calories, chocolate, sugar and fat per serving of each of the four foods.
    let macros: [[i32; 4]; 4] = [
        [400, 200, 150, 500],
        [3, 2, 0, 0],
        [2, 2, 4, 4],
        [2, 4, 1, 5],
    ];

    // 0..10000 servings and 0..1000 cents are the bounds the reference declares.
    let x: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, 10000)).collect();
    for (row, &least) in macros.iter().zip(&limits) {
        // Several macros are zero for some foods; a zero scale would divide by
        // zero inside Pumpkin, so those terms are dropped.
        let terms: Vec<Term> = (0..n)
            .filter(|&j| row[j] != 0)
            .map(|j| x[j].scaled(-row[j]))
            .collect();
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::less_than_or_equals(terms, -least, tag))
            .post();
    }

    let cost = solver.new_bounded_integer(0, 1000);
    let mut spend: Vec<Term> = (0..n)
        .filter(|&j| price[j] != 0)
        .map(|j| x[j].scaled(price[j]))
        .collect();
    spend.push(cost.scaled(-1));
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::equals(spend, 0, tag)).post();

    let mut m = Model::new();
    m.put("cost", cost);
    m.minimise(cost);
    m
}
