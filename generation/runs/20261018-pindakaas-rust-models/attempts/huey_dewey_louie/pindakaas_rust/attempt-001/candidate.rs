// Huey, Dewey and Louie are being questioned by their uncle; they cannot tell a lie.
// Decide who (if any) of Huey, Dewey and Louie is guilty.

fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    // Boolean variables: guilty(Huey), guilty(Dewey), guilty(Louie).
    let h = s.new_lit();
    let d = s.new_lit();
    let l = s.new_lit();

    // Huey: "Dewey and Louie has equal share in it; if one is guilty, so is the other."
    // Equal share: Dewey is guilty exactly when Louie is guilty.
    s.add_clause([!d, l])?;
    s.add_clause([d, !l])?;

    // Dewey: "If Huey is guilty, then so am I."
    s.add_clause([!h, d])?;

    // Louie: "Dewey and I are not both guilty."
    s.add_clause([!d, !l])?;

    let mut out = Out::new();
    out.put("huey", h).put("dewey", d).put("louie", l);
    Ok(out)
}
