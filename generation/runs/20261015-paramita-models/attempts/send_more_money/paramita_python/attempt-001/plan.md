Letters s,e,n,d,m,o,r,y each take a digit 0-9 (one-hot per letter): exactly one digit per letter -> sum(xv[v]) == 1
Each letter must be assigned a unique digit -> per digit v: sum over letters of xv[v] <= 1 (all different)
The first letter of each word cannot be zero -> s != 0, m != 0 (not xv[0])
SEND + MORE = MONEY -> 1000*s+100*e+10*n+d + 1000*m+100*o+10*r+e == 10000*m+1000*o+100*n+10*e+y (integer expressions over one-hot digits)
Objective -> none (satisfaction)
