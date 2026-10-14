// Devil's word: put a '+' or a '-' in front of each integer of the array so
// that the signed numbers add up to the given total.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let arr = inst.ints("arr"); // the integers to be signed
    let total = inst.int("total"); // the sum the signed integers must reach
    let n = arr.len();
    let max_val = *arr.iter().max().expect("arr must not be empty");

    // plus[i] is true when arr[i] is added and false when it is subtracted.
    let plus: Vec<Lit> = (0..n).map(|_| solver.new_literal()).collect();

    // result[i] is arr[i] with its sign, so it lies between -max(arr) and max(arr).
    let result: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(-max_val, max_val)).collect();

    // result[i] = arr[i] if plus[i], else -arr[i], i.e.
    // result[i] = 2 * arr[i] * plus[i] - arr[i]. A zero arr[i] has no sign to
    // choose, so its result is simply fixed at 0 (Pumpkin cannot take a zero coefficient).
    let signed = solver.new_constraint_tag();
    for i in 0..n {
        let terms: Vec<Term> = if arr[i] == 0 {
            vec![result[i].scaled(1)]
        } else {
            vec![result[i].scaled(1), plus[i].get_integer_variable().scaled(-2 * arr[i])]
        };
        solver
            .add_constraint(pumpkin_solver::equals(terms, -arr[i], signed))
            .post();
    }

    // The signed numbers add up to the total.
    let terms: Vec<Term> = result.iter().map(|r| r.scaled(1)).collect();
    let sum = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(terms, total, sum))
        .post();

    let mut m = Model::new();
    m.put("result", result);
    m
}
