// 100 bushels among 100 people: 3 per man, 2 per woman, half per child,
// with five times as many women as men.
//
// The puzzle statement fixes every number, so the instance carries no fields;
// the constants below are the problem, not one instance of it.
fn build(_inst: &Instance, cp: &mut Cp) -> Model {
    let men = cp.int(0, 100);
    let women = cp.int(0, 100);
    let children = cp.int(0, 100);

    cp.eq(vec![t(men), t(women), t(children)], 100);
    // Doubled to clear the child's half bushel.
    cp.eq(vec![c(6, men), c(4, women), t(children)], 200);
    cp.eq(vec![c(5, men), c(-1, women)], 0);

    let mut m = Model::new();
    m.put("men", men);
    m.put("women", women);
    m.put("children", children);
    m
}
