<think>
Okay, I need to model this vessel loading problem using CPMpy. Let's start by understanding the problem. The goal is to place three containers on a 5x5 deck without overlapping and respecting separation constraints. Also, the loading sequence requires each container after the first to touch a previous container or the deck's wall both to the north and west. 

First, the input data: deck is 5x5. There are three containers with widths [5,2,3] and lengths [1,4,4]. All are class 1, so the separation constraints between classes might not apply here since the separation matrix for class 1 and 1 is [0,0]. Wait, the separation matrix is given as [[0,0],[0,0]], which probably means between classes 1 and 1, the required separation is 0 in both directions. So maybe no separation constraints here. But I should note that in case the problem changes, but for now, maybe that's not an issue.

The main constraints are the non-overlapping, fitting within the deck, and the loading sequence constraints.

Let me think about the variables. Each container has a position. Let's represent each container by its left, right, top, bottom coordinates. Wait, the problem says to print (left, right, top, bottom) for each container. So for each container, we need variables for left (west side), right (east side), bottom (south side), and top (north side). The deck's coordinates probably have (0,0) at the southwest corner, so the deck spans from (0,0) to (5,5) in width and length. Wait, deck_width is 5, so the maximum x-coordinate (east) is 5. Similarly, deck_length is 5, so the maximum y-coordinate (north) is 5.

Each container's left must be between 0 and deck_width - container's width. Wait, actually, the left is the x-coordinate of the west side, and right is left + width. Similarly, bottom is the y-coordinate of the south side, and top is bottom + length. So for each container i:

left_i + width[i] <= deck_width

bottom_i + length[i] <= deck_length

Also, all containers must be placed such that their right <= deck_width and top <= deck_length.

Now, non-overlapping: For any two containers i and j (i < j?), their positions must not overlap. So for each pair, either:

- The right of i is <= left of j (along the x-axis), or the left of i >= right of j,

AND

- The top of i is <= bottom of j (along the y-axis), or the bottom of i >= top of j.

Alternatively, the containers must not overlap in both x and y directions. So for all i < j:

(cp.sum([ (right_i <= left_j) | (left_i >= right_j), (top_i <= bottom_j) | (bottom_i >= top_i) ])) >= 1 ?

Wait, actually, the correct way is that for two rectangles to not overlap, they must not overlap in both x and y. So the negation of overlapping is that either they don't overlap in x or don't overlap in y. So the non-overlap condition is:

( (right_i <= left_j) | (left_i >= right_j) ) | ( (top_i <= bottom_j) | (bottom_i >= top_j) )

Wait, no. Wait, two rectangles overlap if they overlap in both x and y. So the non-overlap is the negation of that. So:

¬ ( (left_i < right_j) & (left_j < right_i) & (bottom_i < top_j) & (bottom_j < top_i) )

Which can be written as:

( right_i <= left_j ) | ( right_j <= left_i ) | ( top_i <= bottom_j ) | ( top_j <= bottom_i )

So that's the non-overlap condition between any two containers.

Now, the loading sequence constraints. Each container after the first must touch a previous container or the deck wall both to the north and west. Wait, the problem says: "each successive container in the loading sequence must be positioned so that it touches part of another container or a deck wall both to the north and to the west."

Hmm, the loading sequence is the order in which containers are placed. The first container can be placed anywhere, but each subsequent container must touch either a previous container or the deck's wall both to the north and west. Wait, the wording is a bit confusing. Let me parse it again.

"Each successive container in the loading sequence must be positioned so that it touches part of another container or a deck wall both to the north and to the west."

So for container j (after the first), when placed, it must touch either a previous container or the deck's wall in the north direction and also in the west direction. Wait, "both to the north and to the west". So the container must touch something (either a container or the wall) in the north direction and also in the west direction. 

Wait, perhaps the container must be placed such that its north side is adjacent to either the deck's north wall or another container's south side, and its west side is adjacent to the deck's west wall or another container's east side. Or maybe the other way around? Let me think.

Alternatively, the container must be placed such that it is touching either a previous container or the deck wall in both the north and west directions. So for the north direction, the container's top (north side) must be adjacent to either the deck's top (north wall at y=5) or another container's bottom (south side). Similarly, the west side (left) must be adjacent to the deck's west wall (x=0) or another container's right (east side).

Wait, perhaps the container must be placed such that it is adjacent to something (either a container or the wall) in both the north and west directions. So for the north direction, the container's top must be equal to either the deck's length (5) or the bottom of some other container. Similarly, the left must be 0 or the right of some other container.

Alternatively, the container must be placed such that it is adjacent to at least one container or the wall in the north direction and also in the west direction. So for each container after the first, there exists some container before it (in the loading order) such that either:

- The container's left is 0 (west wall) or its left is equal to the right of some previous container (so it's adjacent to the east side of that container).

AND

- The container's bottom is 0 (south wall) or its bottom is equal to the top of some previous container (so it's adjacent to the south side of that container).

Wait, but the problem says "touch part of another container or a deck wall both to the north and to the west". Hmm, perhaps the container must touch a previous container or the wall in the north direction and also in the west direction. So for the north direction, the container's north side (top) must be adjacent to either the deck's north wall (so top = deck_length) or the south side (bottom) of another container. Similarly, the west side (left) must be adjacent to the deck's west wall (left=0) or the east side (right) of another container.

Alternatively, the container must be placed such that it is adjacent to the north wall or a previous container in the north direction, and also adjacent to the west wall or a previous container in the west direction. 

This is a bit ambiguous, but I think the key is that for each container after the first, there must be at least one container before it (in the loading order) such that either:

- The current container's left is equal to the right of some previous container (so they are adjacent on the west side), or the left is 0 (west wall).

AND

- The current container's bottom is equal to the top of some previous container (so they are adjacent on the south side), or the bottom is 0 (south wall).

Wait, but the problem says "touch part of another container or a deck wall both to the north and to the west". The wording is a bit confusing. Let me re-read the problem statement:

"Each successive container in the loading sequence must be positioned so that it touches part of another container or a deck wall both to the north and to the west."

Ah, "both to the north and to the west". So the container must touch something (container or wall) in the north direction and also in the west direction. So for the north direction, the container's north side (top) must be adjacent to either the deck's north wall (so top = deck_length) or the south side (bottom) of another container. Similarly, the west side (left) must be adjacent to the deck's west wall (left=0) or the east side (right) of another container.

Wait, but the north direction is towards the top of the deck. So the container's top must be touching either the deck's top (so top = deck_length) or another container's bottom. Similarly, the west side (left) must be touching the deck's west wall (left=0) or another container's right.

Alternatively, the container must be placed such that it is adjacent to the north wall or a previous container in the north direction, and also adjacent to the west wall or a previous container in the west direction. 

So for each container j (starting from the second), there must exist some container i < j such that either:

- The left of j is equal to the right of i (so they are adjacent on the west side), or left_j is 0 (west wall).

AND

- The bottom of j is equal to the top of i (so they are adjacent on the south side), or bottom_j is 0 (south wall).

Wait, but the problem says "both to the north and to the west". Maybe the north and west directions are the directions from which the container is placed. So the container must be placed such that it is adjacent to the north wall or a previous container in the north direction (i.e., its top is at the deck's top or touching a container's bottom), and also adjacent to the west wall or a previous container in the west direction (left is 0 or touching a container's right).

Alternatively, perhaps the container must be placed such that it is adjacent to the north wall or a previous container in the north direction (so its top is at the deck's top or touching a container's bottom), and also adjacent to the west wall or a previous container in the west direction (left is 0 or touching a container's right). 

This is a bit ambiguous, but I'll proceed with this interpretation.

Now, how to model this in CPMpy. Since the loading sequence is the order of the containers, but the problem doesn't specify the order. Wait, the problem says "the loading sequence may be further constrained by the physical loading sequence. Containers are manoeuvred into position from the southeast corner. Each successive container in the loading sequence must be positioned so that it touches part of another container or a deck wall both to the north and to the west."

Wait, the loading sequence is the order in which the containers are placed. The problem requires that the order must be such that each container after the first is placed according to the constraints. But the problem doesn't give the order; we have to choose the order as part of the solution. So the model must find an order of the containers (permutation) such that when placed in that order, each container after the first satisfies the adjacency constraints.

Ah, right! So the order of the containers is part of the decision variables. Because the problem doesn't specify the order, we have to decide the order as part of the model. Therefore, the model must include a permutation variable indicating the order in which the containers are placed. 

This complicates things because the order is part of the variables. So for each container j (starting from the second in the order), we need to ensure that in the order, the previous containers (those before j in the order) satisfy the adjacency constraints.

Hmm, this is a bit tricky. Let me think of how to model this.

First, we need to decide the order of the containers. Let's denote the order as a permutation of the container indices (0,1,2). Let's call this permutation 'order', where order[0] is the first container, order[1] the second, etc.

Then, for each position k in the order (starting from 1), the container at position k must satisfy the adjacency constraints with the previous containers (those in positions 0 to k-1).

So for each k from 1 to n_containers-1:

container_j = order[k]

We need to ensure that container_j's left is either 0 or equal to the right of some container_i in order[0..k-1], and similarly for the bottom.

Wait, but how to model this in CPMpy? Because for each container_j in the order after the first, there must exist at least one container_i before it in the order such that either:

left_j == right_i OR left_j == 0,

AND

bottom_j == top_i OR bottom_j == 0.

Wait, no, the AND is between the two conditions. Wait, the problem says "touch part of another container or a deck wall both to the north and to the west". So both conditions must be met: the container must touch something in the north direction and in the west direction. So for the west direction (left), it must be touching either a container's right or the west wall. For the north direction (top), it must be touching either a container's bottom or the north wall.

Wait, actually, the north direction is the direction towards the top of the deck. So the container's top (north side) must be adjacent to either the deck's north wall (so top_j = deck_length) or the bottom of some container_i (so top_j = bottom_i). Similarly, the left (west side) must be adjacent to the deck's west wall (left_j = 0) or the right of some container_i (left_j = right_i).

Therefore, for container_j (placed after the first), there must exist at least one container_i (earlier in the order) such that either:

(left_j == right_i) OR (left_j == 0),

AND

(top_j == bottom_i) OR (top_j == deck_length).

Wait, no, the 'AND' is between the two conditions. The container must satisfy both the west and north adjacency conditions. So for each container_j after the first, there must exist at least one container_i (before it in the order) such that:

(left_j == right_i OR left_j == 0) AND (top_j == bottom_i OR top_j == deck_length).

Wait, no, the problem says "touch part of another container or a deck wall both to the north and to the west". So the container must touch something in the north direction (either a container or the wall) AND in the west direction (either a container or the wall). So both conditions must be met. 

Therefore, for container_j, the left must be either 0 or equal to some container_i's right (from before it in the order), and the top must be either deck_length or equal to some container_i's bottom (from before it in the order). 

Wait, but the container can touch different containers for the west and north directions. For example, the left could be touching container A's right, and the top could be touching container B's bottom. So the existence of at least one container for the west and at least one for the north? Or is it that there exists a single container that provides both? 

The problem says "touch part of another container or a deck wall both to the north and to the west". The wording suggests that for both directions (north and west), the container must touch either a container or the wall. So the two conditions (west and north) are separate, but each must be satisfied by either a container or the wall. 

Therefore, for container_j:

Either left_j == 0 or there exists some container_i before it in the order where left_j == right_i,

AND

Either top_j == deck_length or there exists some container_i before it in the order where top_j == bottom_i.

Wait, but the problem says "touch part of another container or a deck wall both to the north and to the west". So the "another container" could be different for each direction. So the two conditions are separate. 

Therefore, the constraints are:

For container_j (after first):

(left_j == 0) OR (exists i < j in order: left_j == right_i)

AND

(top_j == deck_length) OR (exists i < j in order: top_j == bottom_i)

So, the model must enforce these two conditions for each container after the first in the order.

This complicates the model because for each container_j, we have to check existence over the previous containers in the order. 

Hmm, how to model existence in CPMpy? 

First, the order is a permutation variable. Let's denote the order as a list of variables, order = [order_0, order_1, order_2], where order_0 is the first container, etc. 

Alternatively, perhaps it's better to model the order as a permutation array. Let's see.

Alternatively, perhaps we can model the order as a permutation variable. Let's think of the order as a list of indices (0,1,2) in some permutation. 

But in CPMpy, permutation variables can be created with cp.permutation(). 

Wait, in CPMpy, you can create a permutation variable with cp.permutation(n), which is an array of integers from 0 to n-1 in some order. 

So for n_containers =3, order = cp.permutation(3). 

Then, for each position k in 1,2 (since order[0] is first, order[1] is second, order[2] third), we need to enforce the constraints for container_j = order[k].

So for each k in 1,2:

container_j = order[k]

We need to check that:

(left_j == 0) OR (there exists some container_i in order[0..k-1] where left_j == right_i)

AND

(top_j == deck_length) OR (there exists some container_i in order[0..k-1] where top_j == bottom_i)

Hmm, how to model the existence of such a container_i?

The existence can be modeled by saying that the OR over all previous containers of (left_j == right_i) must be true, or left_j is 0. 

Wait, for the west condition:

Either left_j is 0, or there exists at least one container_i in the previous containers (those before k in the order) such that left_j == right_i.

Similarly for the north condition.

So for the west condition:

cp.any( [ left_j == right_i for i in previous_containers ] ) OR (left_j == 0)

Wait, but in CPMpy, the 'any' function is part of the library. Wait, the user guidelines say to use cp.any instead of Python's any. 

Wait, the user guidelines mention: "Use cp.sum, cp.all, cp.any instead of Python built-in functions."

So, for the west condition:

cp.any( [ left_j == right_i for i in previous_containers ] ) | (left_j == 0)

Wait, but how to get the previous containers? The previous containers are those in order[0..k-1], but the order is a permutation variable. So the indices of the containers before k in the order are the elements of order[0], order[1], ..., order[k-1].

Wait, but the order is a permutation variable, so for each k, the previous containers are the containers with indices in order[0..k-1].

Therefore, for container_j = order[k], the previous containers are the containers with indices in order[0], order[1], ..., order[k-1].

But in CPMpy, variables can't be used in loops like this. Because the order is a variable, not a known list. 

Hmm, this is a problem. Because the existence condition depends on the order, which is a variable. So we can't loop over the previous containers in the order because the order is part of the variables. 

This complicates things. 

Alternative approach: For each container j (not the first in the order), we can model the existence condition by considering all possible previous containers (all other containers except j itself) and ensuring that either the west condition is met by the deck or by any of the previous containers in the order. 

Wait, but how to model the order's effect here?

Alternatively, perhaps we can model for each container j (except the first in the order), the existence of at least one container i (any of the other containers) such that i is placed before j in the order, and either:

left_j == right_i or left_j ==0,

and similarly for the top.

But this seems difficult because the order is a variable. 

Hmm, perhaps we can model this by introducing auxiliary variables for the order and then for each container, track whether it is before another in the order. 

Alternatively, perhaps it's better to model the order as a permutation variable and for each container j (except the first in the permutation), enforce the constraints based on all other containers, but with the condition that at least one of them is before it in the order and satisfies the adjacency.

Wait, perhaps for each container j (not the first in the permutation), we can write:

left_j == 0 OR (there exists some container i != j such that (order_i < order_j) and (left_j == right_i))

Similarly for the top condition.

But how to model this in CPMpy?

Alternatively, for each pair of containers i and j (i != j), we can have a variable indicating whether i is before j in the order. But that might be too many variables.

Alternatively, for each container j (not first in order), the west condition can be written as:

left_j == 0 OR (sum over all i != j of ( (order_i < order_j) & (left_j == right_i) )) >= 1 )

Similarly for the top condition.

Wait, but in CPMpy, the order is a permutation variable. Let me think of order as an array where order[0], order[1], order[2] are the indices of the containers in the order. 

So for container j (which is at position k in the order), the previous containers are those with indices in order[0..k-1].

But since the order is a variable, we can't directly loop over the previous containers. 

Hmm, perhaps the following approach:

For each container j (except the first in the permutation), we can model the west condition as:

left_j == 0 OR (there exists some container i such that i is placed before j in the order and left_j == right_i )

Similarly for the top condition.

To model existence, we can use a big OR over all possible i (other than j) of ( (order_i < order_j) & (left_j == right_i) )

But in CPMpy, the order is a permutation variable, so for each i and j, the condition (order_i < order_j) is a boolean expression. 

Wait, but in CPMpy, variables can't be compared directly in that way. Wait, the order is an array of integers (indices 0,1,2). So for each i and j, the condition (order[i] < order[j]) is a boolean expression. Wait no, order is a permutation variable, so order is an array of variables. So for each i and j, order[i] is a variable, so comparing them would require a constraint. 

Alternatively, perhaps for each pair of containers i and j (i != j), we can have a variable indicating whether i comes before j in the order. But that's a lot of variables. 

Alternatively, for each container j (not first in the permutation), the west condition can be written as:

left_j == 0 OR (cp.any( [ (order_i < order_j) & (left_j == right_i) for i in 0..2 if i != j ] ) )

Wait, but in code, how to do this?

Alternatively, for each container j (except the first in the permutation), the west condition is:

cp.ifthenelse( left_j != 0, cp.any( [ (order_i < order_j) & (left_j == right_i) for i in range(n_containers) if i != j ] ), True )

Wait, but this is getting complicated. 

Alternatively, perhaps the following approach:

For each container j (not first in the permutation), the west condition is:

left_j == 0 OR (cp.any( [ (order_i < order_j) & (left_j == right_i) for i in range(n_containers) if i != j ] ) )

Similarly for the top condition.

But how to code this in CPMpy?

Let me think step by step.

First, the order is a permutation variable of the containers. Let's define it as:

order = cp.permutation(n_containers)

Then, for each container j in 0..2 (since n_containers=3), except the first in the order, we need to check the constraints. Wait, but how to find which containers are not first in the order?

Alternatively, for each j in 0..2, we can check if it is not the first in the order. But that's not straightforward. 

Alternatively, for each j in 0..2, we can consider all other containers i and see if i is before j in the order. 

Alternatively, perhaps it's better to loop over each position in the order (except the first) and handle the container at that position. 

The order is an array of variables, so for each position k in 1,2 (since the first position is 0), the container at position k is order[k]. 

So for each k in 1,2:

current_container = order[k]

Then, the previous containers are those in order[0], order[1], ..., order[k-1].

But how to get their indices? 

Wait, the current_container is the index of the container (0,1,2). The previous containers are the containers with indices in order[0..k-1].

So for the current_container (say, j), the previous containers are the containers with indices in order[0], order[1], ..., order[k-1].

But in code, how to get the indices of those containers?

Alternatively, for each container j (current_container), the previous containers are all containers i where order.index(i) < k. 

Wait, but in CPMpy, the order is a permutation variable, so we can't compute its indices. 

Hmm, this is getting really complicated. Maybe I need to think of another way.

Alternative Idea: Instead of using a permutation variable for the order, perhaps model the order as a list of variables indicating the position of each container. For example, pos is an array of variables where pos[j] is the position in the order (0,1,2) for container j. Then, the order is determined by the pos array. 

But then, we need to ensure that all pos[j] are distinct and form a permutation. 

Alternatively, perhaps it's better to model the order as a permutation array, and then for each container j, its position in the order is the index in the permutation array where j is located. 

Wait, perhaps the permutation array order is such that order[0] is the first container, order[1] the second, etc. So for container j, its position in the order is the index where order[i] == j. 

But in code, this would require for each j, a variable indicating its position. 

Alternatively, perhaps the following approach:

Let me try to code this step by step.

First, define the variables for each container's position:

Each container has left, right, bottom, top. Since the width and length are known, right = left + width[j], top = bottom + length[j].

Wait, yes. So for container j:

left_j is a variable between 0 and deck_width - width[j]

Similarly, bottom_j is between 0 and deck_length - length[j]

right_j = left_j + width[j]

top_j = bottom_j + length[j]

So, the variables can be defined as left and bottom for each container, and right and top are expressions.

Therefore, for each container j:

left_j = cp.intvar(0, deck_width - width[j], name=f"left_{j}")

bottom_j = cp.intvar(0, deck_length - length[j], name=f"bottom_{j}")

right_j = left_j + width[j]

top_j = bottom_j + length[j]

Now, the non-overlapping constraints between all pairs of containers.

For all pairs (i,j) where i < j:

Either:

right_i <= left_j OR left_i >= right_j,

OR

top_i <= bottom_j OR bottom_i >= top_j.

So, for each pair (i,j):

cp.element( (right_i <= left_j) | (left_i >= right_j) | (top_i <= bottom_j) | (bottom_i >= top_j) )

Wait, but in CPMpy, the constraints are added as expressions. So for each pair, we can add the constraint:

(cp.sum( [ (right_i <= left_j), (left_i >= right_j), (top_i <= bottom_j), (bottom_i >= top_j) ] ) >= 1 )

Wait, no. The correct way is to express that at least one of the four conditions must hold. 

Alternatively, the non-overlap condition is equivalent to:

( (right_i <= left_j) | (left_i >= right_j) ) | ( (top_i <= bottom_j) | (bottom_i >= top_j) )

So, the constraint is:

( (right_i <= left_j) | (left_i >= right_j) ) | ( (top_i <= bottom_j) | (bottom_i >= top_j) )

This can be written as a logical OR of the two terms.

Now, moving on to the loading sequence constraints.

We need to model the order in which containers are placed. Let's define the order as a permutation variable:

order = cp.permutation(n_containers)

Then, for each position k in 1, 2 (since the first is 0), the container at that position (order[k]) must satisfy the adjacency constraints with the previous containers (those in order[0..k-1]).

So for each k in 1, 2:

current_container = order[k]

prev_containers = [order[0], order[1], ..., order[k-1]]

We need to ensure that:

Either left_current == 0 OR there exists some container in prev_containers where left_current == right_prev_container,

AND

Either top_current == deck_length OR there exists some container in prev_containers where top_current == bottom_prev_container.

Hmm, how to model this?

First, for the left condition:

left_current is either 0, or for some prev_container in prev_containers, left_current == right_prev_container.

Similarly for the top condition.

To model existence, for the left condition:

cp.any( [ left_current == right[prev_container] for prev_container in prev_containers ] ) | (left_current == 0)

Similarly for the top condition:

cp.any( [ top_current == bottom[prev_container] for prev_container in prev_containers ] ) | (top_current == deck_length)

But in code, how to loop over prev_containers?

Wait, prev_containers are the containers in order[0..k-1], but since order is a permutation variable, we can't directly loop over them. 

Hmm, perhaps the following approach:

For each k in 1,2:

current_j = order[k]

prev_positions = [0..k-1]

prev_containers = [order[p] for p in prev_positions]

But since order is a variable array, this can't be done directly. 

Alternative Idea: For each container j (except the first in the permutation), we can model the constraints by considering all other containers i and check if i is before j in the order. 

For each container j (0,1,2):

if j is not the first in the order (i.e., there exists some k where order[k] = j and k >0), then:

left_j must be 0 or equal to the right of some container i that is before j in the order.

Similarly for the top.

But how to express this?

Alternatively, for each container j (not first in the order):

left_j == 0 OR (there exists an i != j such that (order.index(i) < order.index(j)) and (left_j == right_i) )

Similarly for the top.

But in CPMpy, the order.index(i) is not directly accessible as a variable. 

Hmm, perhaps we can model for each pair of containers i and j (i != j):

if i is before j in the order, then the adjacency conditions can be considered. 

Alternatively, for each container j (not first in the order), the left condition is:

left_j == 0 OR (cp.any( [ (order_i < order_j) & (left_j == right_i) for i in 0..2 if i != j ] ) )

Wait, but how to express order_i < order_j? 

Wait, order is a permutation array. For each i and j, the position of container i in the order is the index where order[k] = i. 

Alternatively, for each pair of containers i and j (i != j), we can have a variable indicating whether i comes before j in the order. Let's call this before[i][j]. 

But this would require n_containers^2 variables, which for n=3 is manageable. 

Let me try this approach.

Define before as a 2D array of boolean variables, where before[i][j] is True if container i comes before container j in the order. 

Then, for all i != j, before[i][j] is equivalent to (order.index(i) < order.index(j)). 

But how to model this?

Alternatively, the permutation order can be used to define before[i][j] as (order.index(i) < order.index(j)). 

But in CPMpy, the permutation variable's indices are variables, so this is not straightforward. 

Alternatively, for each pair i,j, before[i][j] is a boolean variable, and we can add constraints:

for all i,j:

before[i][j] == (order.index(i) < order.index(j))

But I don't think CPMpy allows this directly. 

Hmm, this is getting too complicated. Maybe I should look for another way.

Alternative Idea: Since the order is a permutation variable, for each container j (not first in the permutation), the previous containers are all containers except those after it in the permutation. 

Wait, perhaps for each container j, the position in the permutation is pos_j = the index where order[pos_j] = j. 

Then, for j to not be first, pos_j must be >0. 

Then, the left condition is:

left_j ==0 OR (there exists an i such that pos_i < pos_j and left_j == right_i )

Similarly for the top condition.

But how to model pos_j?

pos is an array of variables where pos[j] is the position of container j in the order. 

So pos is an array of variables such that for all j, pos[j] is in 0..2, and all pos[j] are distinct. 

This can be modeled as:

pos = cp.intvar(0, n_containers-1, shape=n_containers)

model += cp.AllDifferent(pos)

Then, for each j, the position of container j is pos[j], and the order is determined by the pos array. 

Wait, but the order array can be derived from pos as order = [j for j in sorted(range(n_containers), key=lambda x: pos[x])]

But in CPMpy, this is not directly possible. 

Alternatively, the permutation order can be expressed as:

for all j, order[pos[j]] = j 

Wait, no. 

Alternatively, the permutation array order is such that for each position k in 0..2, order[k] is the container at position k. 

Then, the position of container j is the k where order[k] = j. 

So pos[j] = the k where order[k] = j. 

This can be modeled with:

for each j in 0..2:

cp.element( [ (order[k] == j) for k in 0..2 ], pos[j] ) 

Wait, perhaps using a helper variable for pos[j], but this might be complex. 

Alternatively, perhaps it's better to use the pos array as the inverse of the order array. 

Let me think of pos as an array where pos[j] is the position of container j in the order. 

Then, the order array can be defined as:

order = [ cp.intvar(0, n_containers-1) for _ in range(n_containers) ]

model += [ cp.AllDifferent(order) ]

model += [ order[pos[j]] == j for j in 0..2 ]

Wait, no. 

Alternatively, for each position k in 0..2:

order[k] is the container at position k. 

Then, for each container j, pos[j] is the k where order[k] = j. 

So:

for each j in 0..2:

cp.sum( [ (order[k] == j) * (k) for k in 0..2 ] ) == pos[j]

But this requires multiplication of variables, which is not allowed in CPMpy. 

Hmm, this is getting too involved. Maybe I should try to proceed with the permutation variable and see if I can model the constraints without explicitly referencing the previous containers.

Let me try to proceed step by step.

First, define the variables for each container's left and bottom:

n_containers = 3

deck_width =5

deck_length=5

width = [5,2,3]

length = [1,4,4]

classes = [1,1,1]

separation = [[0,0],[0,0]]

We can define for each container j:

left_j = cp.intvar(0, deck_width - width[j], name=f"left_{j}")

bottom_j = cp.intvar(0, deck_length - length[j], name=f"bottom_{j}")

right_j = left_j + width[j]

top_j = bottom_j + length[j]

Then, the non-overlapping constraints between all pairs:

for i in range(n_containers):

    for j in range(i+1, n_containers):

        # Non-overlap between i and j

        model += ( (right_i <= left_j) | (left_i >= right_j) ) | ( (top_i <= bottom_j) | (bottom_i >= top_j) )

Now, the loading sequence constraints.

Define the order as a permutation variable:

order = cp.permutation(n_containers)

Then, for each position k in 1,2 (since the first is 0):

current_j = order[k]

prev_containers = [order[0], order[1], ..., order[k-1]]

We need to ensure that:

left_current_j is either 0 or equal to the right of any of the previous containers.

Similarly for the top.

But how to express this?

For the left condition:

left_current_j ==0 OR (there exists a container in prev_containers where left_current_j == right of that container)

Similarly for the top.

To model existence, for each container in prev_containers, we can check if left_current_j == right of that container. 

But since prev_containers are the first k elements of the order array, which is a permutation variable, we can't directly loop over them. 

Alternative Idea: For each container j (not first in the order), the left condition can be written as:

left_j ==0 OR (there exists an i in 0..2 (i != j) such that (order.index(i) < order.index(j)) and (left_j == right_i) )

Similarly for the top.

But how to model this in CPMpy?

Let me think of the permutation order as an array. For container j, its position in the order is pos_j = the index where order[pos_j] = j. 

Then, the condition for being not first is pos_j >0.

The left condition is:

left_j ==0 OR (there exists an i such that pos_i < pos_j and left_j == right_i )

Similarly for the top.

To model this, we can introduce for each j:

left_ok[j] = (left_j ==0) OR (cp.any( [ (pos_i < pos_j) & (left_j == right_i) for i in 0..2 if i !=j ] ) )

Similarly for top_ok[j].

Then, for each j, if pos_j >0, then left_ok[j] and top_ok[j] must be true.

But how to model pos_j?

pos is an array of variables where pos[j] is the position of container j in the order. 

pos can be defined as:

pos = cp.intvar(0, n_containers-1, shape=n_containers)

model += [ cp.AllDifferent(pos) ]

model += [ order[pos[j]] == j for j in range(n_containers) ]

Wait, this might work. 

Let me explain:

order is the permutation array (order[0], order[1], order[2] are the containers in order).

pos[j] is the position of container j in the order. 

So for each j, order[pos[j]] must equal j. 

This requires:

for each j in 0..2:

order[pos[j]] == j 

This can be added as constraints.

Then, pos is an array of variables indicating the position of each container.

Now, for each j, if pos[j] >0 (i.e., not first in the order), then:

left_ok[j] = (left_j ==0) OR (cp.any( [ (pos[i] < pos[j]) & (left_j == right_i) for i in 0..2 if i !=j ] ) )

Similarly for top_ok[j].

Then, the constraints are:

for each j in 0..2:

if pos[j] >0:

    model += left_ok[j]

    model += top_ok[j]

But how to model the 'if' condition?

We can use implication:

model += (pos[j] >0).implies( left_ok[j] & top_ok[j] )

Wait, but in CPMpy, the implication is a method. 

So:

model += ( (pos[j] >0) ).implies( left_ok[j] & top_ok[j] )

But first, we need to define left_ok[j] and top_ok[j] as expressions.

Let me try to code this.

First, define pos:

pos = cp.intvar(0, n_containers-1, shape=n_containers)

model += cp.AllDifferent(pos)

for j in range(n_containers):

    model += order[pos[j]] == j 

Then, for each j:

left_ok = (left_j ==0) 

for i in range(n_containers):

    if i !=j:

        left_ok |= ( (pos[i] < pos[j]) & (left_j == right_i) )

Similarly for top_ok:

top_ok = (top_j == deck_length)

for i in range(n_containers):

    if i !=j:

        top_ok |= ( (pos[i] < pos[j]) & (top_j == bottom_i) )

Then, the constraint is:

model += ( (pos[j] >0) ).implies( left_ok & top_ok )

Wait, but in code, this would be:

for j in range(n_containers):

    # Compute left_ok and top_ok

    left_ok = (left[j] == 0)

    for i in range(n_containers):

        if i != j:

            left_ok |= ( (pos[i] < pos[j]) & (left[j] == right[i]) )

    top_ok = (top[j] == deck_length)

    for i in range(n_containers):

        if i != j:

            top_ok |= ( (pos[i] < pos[j]) & (top[j] == bottom[i]) )

    # Now, the implication

    model += ( (pos[j] > 0) ).implies( left_ok & top_ok )

Wait, but in CPMpy, the variables are expressions, so the comparisons like pos[i] < pos[j] are expressions that evaluate to a boolean variable. 

However, in CPMpy, the comparison between two integer variables (pos[i] and pos[j]) can be done using the overloaded operators. 

So pos[i] < pos[j] is a boolean expression. 

The & operator between two expressions is the logical AND. 

The | operator is the logical OR. 

So this should work. 

But this requires nested loops over all i and j, which for n=3 is manageable. 

Now, putting this all together.

Now, the separation constraints between classes. 

The separation matrix is given as separation = [[0,0],[0,0]]. 

The classes are all 1, so the separation between class 1 and 1 is 0 in both directions. 

So the separation constraints are not needed here. 

But in general, for two containers of classes c1 and c2, the separation between them must be at least separation[c1-1][c2-1] in one direction and separation[c2-1][c1-1] in the other? Or perhaps the separation is in both directions? 

The problem says: "certain classes of containers are constrained to be separated by minimum distances either along the deck or across the deck."

Assuming that separation between classes c and d requires that the distance between any two containers of those classes must be at least separation[c-1][d-1] in one direction (e.g., along the deck's length) and separation[d-1][c-1] in the other direction (across the deck's width). 

But since in this problem all classes are 1, and the separation between them is 0, we can ignore this constraint for now. 

Thus, the separation constraints are not needed here. 

Now, putting all together.

The code outline would be:

import cpmpy as cp
import json

# Data
deck_width =5
deck_length=5
n_containers =3
width = [5,2,3]
length = [1,4,4]
classes = [1,1,1]
separation = [[0,0],[0,0]]

# Model definition
model = cp.Model()

# Decision variables
order = cp.permutation(n_containers)
pos = cp.intvar(0,