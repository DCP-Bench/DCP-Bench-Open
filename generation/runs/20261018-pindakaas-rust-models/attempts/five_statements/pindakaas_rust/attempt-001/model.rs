// Problem: five_statements. Five statements, numbered 1 to 5. Statement i says
// "Exactly i of these statements are false". Output statements[i] is 1 when
// statement i is true and 0 when it is false, in the input order.

fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n: usize = 5;
    let st: Vec<Lit> = (0..n).map(|_| s.new_lit()).collect();

    // Number of true statements.
    let mut t = LinExp::default();
    for l in &st {
        t += LinExp::from(l.clone());
    }

    // Exactly i of these statements are false, i.e. exactly 5 - i are true.
    // Statement i holds exactly when that count holds.
    for i in 1..=n {
        let holds = reify_eq(s, t.clone(), (n - i) as i64)?;
        let a = st[i - 1].clone();
        s.add_clause([!a.clone(), holds.clone()])?;
        s.add_clause([a, !holds])?;
    }

    let mut out = Out::new();
    out.put("statements", &st);
    Ok(out)
}
