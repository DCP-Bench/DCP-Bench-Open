Basically you start with [0], then you build this list by using one of three
operations: adding 5, adding 7, or taking sqrt. You successfully complete the
game when you have managed to build a list such that 2,10 and 14 appear
on the list, in that order, and there can be other numbers between them.

The rules also require that all the elements are distinct, they're all <=60
and are all only integers. For example, starting with [0], you can
apply (add5, add7, add5), which would result in [0, 5, 12, 17], but since
it doesn't have 2,10,14 in that order it doesn't satisfy the game.

Print the sequence of integers (x) that satisfies the above conditions in the correct order starting from 0, ending with 14, and has length of 24.
