// Heterosquare of order n: an n*n square x whose elements are distinct integers
// from 1 to n^2 such that the sums of the rows, columns and diagonals are all different.
// The instance gives the order n. Output x as a list of lists of integers.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.size("n");
    let nn = (n * n) as i64;

    // a square of integer variables, each element from 1 to n^2
    let mut x: Vec<Vec<IntVar>> = Vec::with_capacity(n);
    for _ in 0..n {
        let mut row: Vec<IntVar> = Vec::with_capacity(n);
        for _ in 0..n {
            row.push(IntVar::new(1..=nn));
        }
        x.push(row);
    }

    // the elements of the square are distinct integers from 1 to n^2
    let cells: Vec<IntVar> = x.iter().flatten().cloned().collect();
    all_different(s, &cells)?;

    let mut sums: Vec<IntVar> = Vec::new();

    // the sums of the rows
    for i in 0..n {
        let mut e = LinExp::default();
        for j in 0..n {
            e += iv(&x[i][j]);
        }
        sums.push(define(s, e)?);
    }

    // the sums of the columns
    for j in 0..n {
        let mut e = LinExp::default();
        for i in 0..n {
            e += iv(&x[i][j]);
        }
        sums.push(define(s, e)?);
    }

    // the sums of the diagonals
    let mut main_diag = LinExp::default();
    let mut anti_diag = LinExp::default();
    for i in 0..n {
        main_diag += iv(&x[i][i]);
        anti_diag += iv(&x[i][n - 1 - i]);
    }
    sums.push(define(s, main_diag)?);
    sums.push(define(s, anti_diag)?);

    // the sums of the rows, columns and diagonals are all different
    all_different(s, &sums)?;

    let mut out = Out::new();
    out.put("x", &x);
    Ok(out)
}
