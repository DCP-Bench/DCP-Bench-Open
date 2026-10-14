// Dudeney numbers: find a number larger than 1, with at most n digits, that is a
// perfect cube whose digit sum equals its cube root.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.size("n");

    // The number has n digits (leading zeros allowed), so it is below 10^n, and
    // its digit sum, which is its cube root, is at most 9n (the reference's bounds).
    let largest: i32 = (0..n).fold(1i32, |acc, _| acc * 10) - 1;
    let digits: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, 9)).collect();
    let number = solver.new_bounded_integer(0, largest);
    let cube_root = solver.new_bounded_integer(1, 9 * n as i32);

    // The number is the cube of cube_root: square = cube_root^2, number = square * cube_root.
    let cube = solver.new_constraint_tag();
    let square = solver.new_bounded_integer(1, 81 * (n * n) as i32);
    solver.add_constraint(pumpkin_solver::times(cube_root, cube_root, square, cube)).post();
    solver.add_constraint(pumpkin_solver::times(square, cube_root, number, cube)).post();

    // The cube root is the sum of the digits.
    let digit_sum = solver.new_constraint_tag();
    let mut terms: Vec<Term> = digits.iter().map(|d| d.scaled(1)).collect();
    terms.push(cube_root.scaled(-1));
    solver.add_constraint(pumpkin_solver::equals(terms, 0, digit_sum)).post();

    // The digits spell the number: number = sum digits[i] * 10^(n-1-i).
    let place_value = solver.new_constraint_tag();
    let mut terms: Vec<Term> = Vec::new();
    let mut weight = 1;
    for i in (0..n).rev() {
        terms.push(digits[i].scaled(weight));
        if i > 0 {
            weight *= 10;
        }
    }
    terms.push(number.scaled(-1));
    solver.add_constraint(pumpkin_solver::equals(terms, 0, place_value)).post();

    // The number is larger than 1 (written as -number <= -2).
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::less_than_or_equals(vec![number.scaled(-1)], -2, tag))
        .post();

    let mut m = Model::new();
    m.put("number", number);
    m
}
