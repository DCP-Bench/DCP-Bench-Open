At the hospital n people are on a waiting list for a kidney’s transplant. We have the information about the
compatibility between these people as a directed graph: compatible[i] is the set of people to which i can donate.
Given this information, we want to maximize the number of people that receive a new kidney: anyone who gives a kidney
must receive one, and no person receives more than one kidney.

Print the transplants (transplants) as a list of lists, where transplants[i][j] is 1 if person i donates to person j,
and 0 otherwise.
