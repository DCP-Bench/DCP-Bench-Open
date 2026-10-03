// Equal sized groups: split a sorted list of n elements into k groups by
// choosing k - 1 break points, keeping equal values in the same group, so that
// the group sizes are as close as possible to the ideal size round(n / k).
// The total error is the sum over groups of |group size - ideal size|.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let a = inst.ints("a"); // the sorted elements
    let k = inst.size("k"); // number of groups
    let n = a.len() as i32;

    // The ideal group size round(n / k), rounding a half to the even integer as
    // Python's round does in the reference.
    let (quotient, remainder) = (n / k as i32, n % k as i32);
    let ideal = if 2 * remainder < k as i32 {
        quotient
    } else if 2 * remainder > k as i32 || quotient % 2 != 0 {
        quotient + 1
    } else {
        quotient
    };

    // x[p] is the break point p: the number of elements before the break, so the
    // elements are cut between position x[p] - 1 and x[p] (counting from 0).
    // Equal values must stay in the same group, so a break may not fall between
    // two elements with the same value: x[p] = j is allowed only when
    // a[j - 1] != a[j]. The reference leaves j = n unconstrained (a break after
    // the last element), which the group sizes then rule out.
    let allowed: Vec<i32> = (1..=n)
        .filter(|&j| j == n || a[(j - 1) as usize] != a[j as usize])
        .collect();
    let x: Vec<Var> = (0..k - 1).map(|_| solver.new_sparse_integer(allowed.clone())).collect();

    // s[i] is the size of group i, at least 1 and at most n.
    let s: Vec<Var> = (0..k).map(|_| solver.new_bounded_integer(1, n)).collect();

    // The first group ends at the first break point, so its size is x[0].
    let sizes = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(vec![s[0].scaled(1), x[0].scaled(-1)], 0, sizes))
        .post();
    // A middle group lies between two break points: s[i] = x[i] - x[i - 1].
    for i in 1..k - 1 {
        solver
            .add_constraint(pumpkin_solver::equals(
                vec![s[i].scaled(1), x[i].scaled(-1), x[i - 1].scaled(1)], 0, sizes))
            .post();
    }
    // The last group is what is left after the last break point: s[k-1] = n - x[k-2].
    solver
        .add_constraint(pumpkin_solver::equals(
            vec![s[k - 1].scaled(1), x[k - 2].scaled(1)], n, sizes))
        .post();

    // The error of group i is |s[i] - ideal|. gap[i] = s[i] - ideal lies between
    // 1 - ideal and n - ideal; its absolute value is error[i].
    let gap_tag = solver.new_constraint_tag();
    let abs_tag = solver.new_constraint_tag();
    let mut errors: Vec<Var> = Vec::new();
    for i in 0..k {
        let gap = solver.new_bounded_integer(1 - ideal, n - ideal);
        solver
            .add_constraint(pumpkin_solver::equals(
                vec![s[i].scaled(1), gap.scaled(-1)], ideal, gap_tag))
            .post();
        let error = solver.new_bounded_integer(0, (n - ideal).max(ideal - 1).max(0));
        solver
            .add_constraint(pumpkin_solver::absolute(gap, error, abs_tag))
            .post();
        errors.push(error);
    }

    // z is the total error, between 0 and n as in the reference; it is minimised.
    let z = solver.new_bounded_integer(0, n);
    let mut terms: Vec<Term> = errors.iter().map(|e| e.scaled(1)).collect();
    terms.push(z.scaled(-1));
    let total = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(terms, 0, total))
        .post();

    let mut m = Model::new();
    m.put("x", x);
    m.minimise(z);
    m
}
