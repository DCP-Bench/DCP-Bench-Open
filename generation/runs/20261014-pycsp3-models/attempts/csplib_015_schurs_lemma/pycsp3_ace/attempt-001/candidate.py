from pycsp3 import *

# put the balls 1 to n into c boxes so that no triple x + y = z has all three balls in the same box
n = data.n
c = data.c

# inbox[i][j] is 1 if ball i + 1 is in box j + 1
inbox = VarArray(size=[n, c], dom={0, 1})

# balls[i] is the box of ball i + 1, from 1 to c
balls = VarArray(size=n, dom=range(1, c + 1))

satisfy(
    # a ball must be in exactly one box
    [Sum(inbox[i]) == 1 for i in range(n)],
    # the box number of each ball
    [balls[i] == Sum((j + 1) * inbox[i][j] for j in range(c)) for i in range(n)],
    # for any x, y with x + y = z, the three balls cannot all be in the same box
    [Sum(inbox[x - 1][j], inbox[y - 1][j], inbox[x + y - 1][j]) <= 2
     for x in range(1, n + 1) for y in range(x, n + 1) if x + y <= n for j in range(c)],
    # the boxes are interchangeable, so ball 1 is put in box 1
    inbox[0][0] == 1,
)
