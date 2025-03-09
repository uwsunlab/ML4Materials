---
title: "Python Basics"
date: 2025-02-28
layout: default
parent: Python Tutorials
---


# Python Basics

Here are some common Python syntax we will use.

---

## 📌 1. Printing Output
```python
print("Hello, World!")
```

---

## 📌 2. Variables and Data Types
```python
# Strings
name = "Alice"

# Integers
age = 25

# Floats
height = 5.7

# Booleans
is_student = True
```

---

## 📌 3. Comments
```python
# This is a single-line comment

"""
This is a
multi-line comment
"""
```

---

## 📌 4. Lists
```python
fruits = ["apple", "banana", "cherry"]
print(fruits[0])      # Access item
fruits.append("kiwi") # Add item
```

---

## 📌 5. Tuples
```python
coordinates = (10, 20)
print(coordinates[1])
```

---

## 📌 6. Dictionaries
```python
person = {"name": "Bob", "age": 30}
print(person["name"])
person["age"] = 31
```

---

## 📌 7. Conditional Statements
```python
x = 10
if x > 5:
    print("x is greater than 5")
elif x == 5:
    print("x is 5")
else:
    print("x is less than 5")
```

---

## 📌 8. Loops

### For Loop
```python
for i in range(5):
    print(i)
```

### While Loop
```python
count = 0
while count < 5:
    print(count)
    count += 1
```

---

## 📌 9. Functions
```python
def greet(name):
    print(f"Hello, {name}!")

greet("Alice")
```

---

## 📌 10. Basic Input
```python
name = input("Enter your name: ")
print("Hello", name)
```

---

## 📌 11. Error Handling
```python
try:
    x = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero")
```

---

## 📌 12. Importing Modules
```python
import math
print(math.sqrt(16))
```
