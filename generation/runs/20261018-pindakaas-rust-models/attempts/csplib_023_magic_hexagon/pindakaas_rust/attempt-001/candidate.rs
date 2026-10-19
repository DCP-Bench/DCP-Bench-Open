// csplib_023_magic_hexagon: magic hexagon. Arrange the numbers 1 to 19 on the 19 cells
// A..S of a hexagon (rows of 3, 4, 5, 4, 3 cells) so that the sum of the numbers in each
// of the 15 lines (rows and diagonals) equals the magic constant.
//
// Cell order (index into the output LD): A=0 B=1 C=2 D=3 E=4 F=5 G=6 H=7 I=8 J=9 K=10
// L=11 M=12 N=13 O=14 P=15 Q=16 R=17 S=18.
//
// The 15 lines: the five rows (ABC, DEFG, HIJKL, MNOP, QRS), the five diagonals running
// down-right (HMQ, DINR, AEJOS, BFKP, CGL) and the five diagonals running down-left
// (ADH, BEIM, CFJNQ, GKOR, LPS).
const LINES: [&[usize]; 15] = [
    &[0, 1, 2],
    &[3, 4, 5, 6],
    &[7, 8, 9, 10, 11],
    &[12, 13, 14, 15],
    &[16, 17, 18],
    &[7, 12, 16],
    &[3, 8, 13, 17],
    &[0, 4, 9, 14, 18],
    &[1, 5, 10, 15],
    &[2, 6, 11],
    &[0, 3, 7],
    &[1, 4, 8, 12],
    &[2, 5, 9, 13, 16],
    &[6, 10, 14, 17],
    &[11, 15, 18],
];

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.int("NUM_CELLS");
    let magic = inst.int("MAGIC_SUM");
    let cells: Vec<IntVar> = (0..n).map(|_| IntVar::new(1..=n)).collect();

    // arranging the numbers 1 to 19 in a hexagonal pattern
    all_different(s, &cells)?;

    // the sum of the numbers in each of the 15 lines (rows and diagonals) is equal to a magic constant
    for line in LINES.iter() {
        let mut e = LinExp::default();
        for &i in line.iter() {
            e += iv(&cells[i]);
        }
        post(s, e, Comparator::Equal, magic)?;
    }

    let mut out = Out::new();
    out.put("LD", &cells);
    Ok(out)
}
