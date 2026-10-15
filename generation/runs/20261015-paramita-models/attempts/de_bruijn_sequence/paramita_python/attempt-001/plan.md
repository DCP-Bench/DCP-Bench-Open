cyclic sequence of length base^n over an alphabet of size base -> one position per letter, each position one-hot over letters 0..base-1 (x[p][a]), exactly one letter per position, letter value = sum(a * x[p][a]) (output de_bruijn)
every possible length-n string on the alphabet occurs exactly once as a substring -> for each cyclic window i (positions i..i+n-1 mod L) and each word v: wb[i][v] <-> AND of the letters of the window equal to digits of v (base-ary digits of v); exactly one word per window
each length-n string occurs exactly once -> for each word v: sum over windows i of wb[i][v] == 1 (L = base^n windows and L words)
no objective (satisfaction); the sequence is the output de_bruijn
