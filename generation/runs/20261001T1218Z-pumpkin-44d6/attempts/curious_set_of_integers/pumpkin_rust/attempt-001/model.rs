// Curious set of integers: 1, 3, 8 and 120 have the property that the product of
// any two of them is one less than a perfect square. Find a further number
// (at least 0) that keeps the property when added to the set.
//
// n (the size of the set) and max_val (the bound on every number and on every
// square root) come from the instance; the four known members 1, 3, 8, 120 are
// the puzzle's own constants, mirrored from the reference.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.size("n");
    let max_val = inst.int("max_val");
    let known = [1, 3, 8, 120];

    let x: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, max_val)).collect();

    // The numbers of the set are distinct.
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::all_different(x.clone(), tag)).post();

    // The first four are the known members.
    let given = solver.new_constraint_tag();
    for (k, &value) in known.iter().enumerate() {
        solver.add_constraint(pumpkin_solver::equals(vec![x[k]], value, given)).post();
    }

    // For any two members, their product plus one is the square of some p in
    // 0..max_val. The product and the square are bounded by max_val^2, which
    // stays within 32 bits for max_val up to 46340.
    let square = solver.new_constraint_tag();
    let top = max_val * max_val;
    for i in 0..n {
        for j in 0..n {
            if i == j {
                continue;
            }
            let p = solver.new_bounded_integer(0, max_val);
            let p_squared = solver.new_bounded_integer(0, top);
            let product = solver.new_bounded_integer(0, top);
            solver.add_constraint(pumpkin_solver::times(p, p, p_squared, square)).post();
            solver.add_constraint(pumpkin_solver::times(x[i], x[j], product, square)).post();
            solver
                .add_constraint(pumpkin_solver::equals(vec![p_squared.scaled(1), product.scaled(-1)], 1, square))
                .post();
        }
    }

    let mut m = Model::new();
    m.put("number", x[n - 1]);
    m
}
