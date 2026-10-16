Given a collection of integers (nums), find m elements that sum to zero (m read from the instance).
  "a collection of integers" -> nums (instance field, length taken from the instance)
  "find a number of elements" -> x[i] = 1 if element i is selected; the count of selected is m (instance field m)
  "that sum to zero" -> selected values sum to 0: m.scalar(x, nums, "=", 0)
  "print whether each element is selected (indices)" -> out "indices" = BoolVar[] x
Objective: none (satisfaction).
