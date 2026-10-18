// Cryptarithmetic puzzle, solve the operation:
//   B A I J J A J I I A H F C F E B B J E A
//   + D H F G A B C D I D B I F F A G F E J E
//   = G J E G A C D D H F A F J B F I H E E F
// where all letters are distinct digits from 0 to 9, and the first letter of each number cannot be zero.
// Print the digit of each letter (A, B, C, D, E, F, G, H, I, J).

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    // Each letter is a digit from 0 to 9; letters[k] is the letter with index k (A = 0, ..., J = 9).
    let letters: Vec<_> = (0..10).map(|_| m.new_int_decision(0..=9)).collect();

    // all letters are distinct digits
    m.unique(letters.clone()).post()?;

    // the first letter of each number cannot be zero (B, D and G lead the three numbers)
    m.linear(letters[1]).ne(0).post()?;
    m.linear(letters[3]).ne(0).post()?;
    m.linear(letters[6]).ne(0).post()?;

    let w1: Vec<usize> = "BAIJJAJIIAHFCFEBBJEA".bytes().map(|c| (c - b'A') as usize).collect();
    let w2: Vec<usize> = "DHFGABCDIDBIFFAGFEJE".bytes().map(|c| (c - b'A') as usize).collect();
    let w3: Vec<usize> = "GJEGACDDHFAFJBFIHEEF".bytes().map(|c| (c - b'A') as usize).collect();

    // carries[p] is the carry into column p (column 0 is the least significant digit)
    let carries: Vec<_> = (0..=20).map(|_| m.new_int_decision(0..=1)).collect();
    m.linear(carries[0]).eq(0).post()?;
    m.linear(carries[20]).eq(0).post()?;

    // the addition B A I J ... + D H F G ... = G J E G ..., column by column with carries
    for p in 0..20 {
        let a = letters[w1[19 - p]];
        let b = letters[w2[19 - p]];
        let s = letters[w3[19 - p]];
        m.linear(a + b + carries[p] - s - carries[p + 1] * 10).eq(0).post()?;
    }

    let mut out = Out::new();
    out.put("A", letters[0])
        .put("B", letters[1])
        .put("C", letters[2])
        .put("D", letters[3])
        .put("E", letters[4])
        .put("F", letters[5])
        .put("G", letters[6])
        .put("H", letters[7])
        .put("I", letters[8])
        .put("J", letters[9]);
    Ok(out)
}
