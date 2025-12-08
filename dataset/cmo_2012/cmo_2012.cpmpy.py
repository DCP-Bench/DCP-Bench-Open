#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/2012_CMO_problem.py

"""
Given two positive integers a and b, where a - b is a prime number and a × b is a perfect square n^2,
find the smallest value of a no less than a given minimum. Also, b should be larger than 0.

Print the values of a, b, n, and p (a, b, n, p).
"""

# Data
min_a = 2012
max_val = 10000
# End of data

# Import libraries
from cpmpy import *
import json
from math import sqrt

def is_prime(n):
    """Return True if n is prime, False otherwise"""
    if n < 2:
        return False
    for i in range(2, int(sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def primes(n):
    """Return a list of primes less than n"""
    primes_list = []
    for i in range(2, n):
        if is_prime(i):
            primes_list.append(i)
    return primes_list

def member_of(x, val):
    return sum([x[i] == val for i in range(len(x))]) > 0

prime_list = primes(max_val)

a = intvar(min_a, max_val, name="a")
b = intvar(1, max_val, name="b")
n = intvar(0, max_val, name="n")
p = intvar(2, max_val, name="p")

model = Model(minimize=a)

model += member_of(prime_list, p)

model += [a >= b]
model += [p == a - b]
model += [a * b == n * n]

model.solve()

solution = {"a": a.value(), "b": b.value(), "n": n.value(), "p": p.value()}
print(json.dumps(solution))
# End of CPMPy script