# attempt 1: evaluated under overload

This attempt ran while 26 evaluations of the 1.9 GB jump_highs image ran at
once. The instances it lost failed in the Docker CLI calls around the container
(cleanup or inspection "exceeded 15 seconds"), not in the solver, so attempt 2
evaluates the same bytes again with at most six evaluations at a time.
