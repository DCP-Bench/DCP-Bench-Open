// Finding celebrities at a party: guest i knows guest j when graph[i][j] is 1.
// A celebrity is a guest whom everybody at the party knows, and who knows only other celebrities.
// At least one celebrity is present at the party.
// celebrities[i] is 1 when guest i is a celebrity.
fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let graph = inst.matrix("graph");
    let n = graph.len();
    let celeb: Vec<Lit> = (0..n).map(|_| s.new_lit()).collect();

    // a celebrity is a guest whom everybody at the party knows
    for c in 0..n {
        for i in 0..n {
            if i != c && graph[i][c] == 0 {
                s.add_clause([!celeb[c]])?;
            }
        }
    }

    // a celebrity knows only other celebrities
    for c in 0..n {
        for j in 0..n {
            if j != c && graph[c][j] == 1 {
                s.add_clause([!celeb[c], celeb[j]])?;
            }
        }
    }

    // at least one celebrity is present at the party
    s.add_clause(celeb.clone())?;

    let mut out = Out::new();
    out.put("celebrities", &celeb);
    Ok(out)
}
