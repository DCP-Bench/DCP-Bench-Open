Here's a puzzle similar to the one in the puzzle hunt.  The diagram
below is a bunch of weights (A-M) hanging from a system of bars.
Each weight has an integer value between 1 and 13, and the goal is
to figure out what each weight must be for the the diagram below to
balance correctly as shown:

                       |
                       |
           +--+--+--+--+--+--+--+
           |                    |
           |                    |
        +--+--+--+--+--+        |
        |     L        M        |
        |                       |
+--+--+--+--+--+--+     +--+--+--+--+--+
H              |  I     |  J        K  |
              |        |              |
     +--+--+--+--+--+  |     +--+--+--+--+--+
     E              F  |     G              |
                       |                    |
           +--+--+--+--+--+  +--+--+--+--+--+--+
           A              B  C                 D

The rules for this kind of puzzle are:
(1) The weights on either side of a given pivot point must be equal,
  when weighted by the distance from the pivot, and
(2) a bar hanging beneath another contributes it's total weight as
  through it were a single weight.  For instance, the bar on the bottom
  right must have 5*C=D, and the one above it must have 3*G=2*(C+D).

Print the weights (a, b, c, d, e, f, g, h, i, j, k, l, m) that satisfy the conditions above.
