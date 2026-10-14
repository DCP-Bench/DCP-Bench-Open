// Broken weights: a weight of m pounds breaks into n pieces of whole-pound weight
// that can weigh every integral weight from 1 to m on a balance scale.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let m_total = inst.int("m"); // total weight of the unbroken weight
    let n = inst.size("n"); // number of pieces
    let target_count = m_total as usize; // weights 1..m_total must all be weighable

    // weights[j] is the weight of piece j, between 1 and m_total.
    let weights: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(1, m_total)).collect();
    // x[i][j] says where piece j goes when weighing the object of weight i + 1:
    // -1 on the left pan, 1 on the right pan, 0 left off the scale.
    let x: Vec<Vec<Var>> = (0..target_count)
        .map(|_| (0..n).map(|_| solver.new_bounded_integer(-1, 1)).collect())
        .collect();

    // The pieces add up to the unbroken weight.
    let total = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(weights.clone(), m_total, total))
        .post();

    // Every weight from 1 to m_total can be made: for the object of weight i + 1,
    // the signed sum of the pieces on the scale, weights[j] * x[i][j], is i + 1.
    // product[i][j] holds weights[j] * x[i][j] (Pumpkin's `times`), so the
    // balance itself is a plain linear equation.
    let product_tag = solver.new_constraint_tag();
    let balance = solver.new_constraint_tag();
    for i in 0..target_count {
        let mut products: Vec<Var> = Vec::new();
        for j in 0..n {
            let product = solver.new_bounded_integer(-m_total, m_total);
            solver
                .add_constraint(pumpkin_solver::times(weights[j], x[i][j], product, product_tag))
                .post();
            products.push(product);
        }
        solver
            .add_constraint(pumpkin_solver::equals(products, i as i32 + 1, balance))
            .post();
    }

    let mut m = Model::new();
    m.put("weights", weights);
    m
}
