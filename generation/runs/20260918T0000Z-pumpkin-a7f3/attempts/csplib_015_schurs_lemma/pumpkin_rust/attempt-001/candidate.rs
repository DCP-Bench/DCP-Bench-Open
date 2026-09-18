// Put balls 1..n into c boxes so no triple x + y = z shares a box.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let n = inst.size("n");
    let c_boxes = inst.int("c");

    let balls = cp.ints(n, 1, c_boxes);
    for x in 1..n {
        for y in 1..(n - x + 1) {
            let z = x + y;
            if z <= n {
                // At least one of the three pairs differs.
                let xy = cp.bool();
                cp.iff_eq(xy, vec![t(balls[x - 1]), c(-1, balls[y - 1])], 0);
                let xz = cp.bool();
                cp.iff_eq(xz, vec![t(balls[x - 1]), c(-1, balls[z - 1])], 0);
                let yz = cp.bool();
                cp.iff_eq(yz, vec![t(balls[y - 1]), c(-1, balls[z - 1])], 0);
                cp.any(vec![!xy, !xz, !yz]);
            }
        }
    }

    let mut m = Model::new();
    m.put("balls", balls);
    m
}
