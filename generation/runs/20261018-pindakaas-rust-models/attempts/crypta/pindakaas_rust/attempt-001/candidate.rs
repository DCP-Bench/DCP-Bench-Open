// Cryptarithmetic puzzle: solve the operation
//   B A I J J A J I I A H F C F E B B J E A
// + D H F G A B C D I D B I F F A G F E J E
// = G J E G A C D D H F A F J B F I H E E F
// where all letters are distinct digits from 0 to 9, and the first letter of each
// number cannot be zero. Print the digit of each letter (A, B, C, D, E, F, G, H, I, J).

// The three numbers, most significant digit first.
const W1: &str = "BAIJJAJIIAHFCFEBBJEA";
const W2: &str = "DHFGABCDIDBIFFAGFEJE";
const W3: &str = "GJEGACDDHFAFJBFIHEEF";

fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    // The ten letters A..J are digits 0..=9. The leading letters B, D and G cannot be zero.
    // The letters are distinct digits.
    let mut letters: Vec<IntVar> = Vec::new();
    for c in 0..10u8 {
        let lo = if c == 1 || c == 3 || c == 6 { 1 } else { 0 };
        letters.push(IntVar::new(lo..=9));
    }
    all_different(s, &letters)?;

    // Column addition, from the least significant column. carries[i] is the carry out of
    // column i. The carry out of the last column is zero, because the sum has 20 digits.
    let n = 20usize;
    let letter = |w: &str, j: usize| -> usize { (w.as_bytes()[j] - b'A') as usize };
    let mut carries: Vec<IntVar> = Vec::new();
    for _ in 0..n - 1 {
        carries.push(IntVar::new(0..=1));
    }

    // Each column: the sum of the two addends and the carry in equals the result digit
    // plus ten times the carry out.
    // a + b + carry_in = r + 10 * carry_out
    for i in 0..n {
        let j = n - 1 - i;
        let a = &letters[letter(W1, j)];
        let b = &letters[letter(W2, j)];
        let r = &letters[letter(W3, j)];
        let mut e = iv(a) + iv(b) - iv(r);
        if i > 0 {
            e = e + iv(&carries[i - 1]);
        }
        if i < n - 1 {
            e = e - scaled(&carries[i], 10);
        }
        post(s, e, Comparator::Equal, 0)?;
    }

    let mut out = Out::new();
    let names = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"];
    for (k, name) in names.iter().enumerate() {
        out.put(*name, &letters[k]);
    }
    Ok(out)
}
