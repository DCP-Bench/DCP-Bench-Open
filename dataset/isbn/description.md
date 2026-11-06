ISBN-13 Validation and Check Digit Calculation.

Problem:
An ISBN-13 (International Standard Book Number) is a 13-digit number where the last digit is a check digit
calculated from the first 12 digits.  The check digit is calculated as follows:

1.  Multiply the first 12 digits alternately by 1 and 3 (starting with 1).
2.  Sum the products.
3.  The check digit is (10 - (sum % 10)) % 10.

Given a list of 13 integers representing an ISBN-13, where -1 represents an unknown digit,
find the values of the unknown digits such that the resulting number is a valid ISBN-13.
An ISBN-13 must start with 978 or 979.

Print the complete valid isbn (isbn) as a list of integers.
