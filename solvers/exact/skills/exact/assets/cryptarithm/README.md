# Cryptarithm SEND + MORE = MONEY (satisfy)

**Problem:** Give each letter a digit 0-9 so that SEND + MORE = MONEY, different letters get different digits, and no word of more than one letter starts with 0.
**Shows:** a value variable per letter tied to one-hot digit indicators, all-different as "each digit used at most once" over the indicators, a sum written in place values from data, and a satisfaction call.
**Run:** `python3 model.py`
**Expected:** `9567 + 1085 = 10652`
**Expected:** `all letters different: True`
