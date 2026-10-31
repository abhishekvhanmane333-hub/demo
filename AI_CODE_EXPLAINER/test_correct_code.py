def add(a, b):
    result = a + b
    return result

def divide(a, b):
    return a / b

print(add(10, 20))
print(divide(10, 2))


# 01 Student Marks Analysis
def calculate_average(marks):
    total = sum(marks)
    average = total / len(marks)
    return average

def check_result(average):
    if average >= 35:
        return "Pass"
    return "Fail"

marks = [75, 80, 65, 90, 70]
average = calculate_average(marks)
print("Average Marks:", average)
print("Result:", check_result(average))

# 02 Employee Salary Calculator
def calculate_salary(basic, bonus):
    return basic + bonus

def display_employee(name, salary):
    print("Employee Name:", name)
    print("Total Salary:", salary)

name = "Rahul"
basic_salary = 25000
bonus = 3000
total_salary = calculate_salary(basic_salary, bonus)
display_employee(name, total_salary)
print("Salary calculated successfully")

# 03 Shopping Bill Calculator
def calculate_bill(price, quantity):
    total = price * quantity
    return total

def apply_discount(total):
    if total >= 1000:
        return total * 0.90
    return total

price = 500
quantity = 3
total = calculate_bill(price, quantity)
final_amount = apply_discount(total)
print("Total Bill:", total)
print("Final Amount:", final_amount)

# 04 Even and Odd Number Checker
def check_number(number):
    if number % 2 == 0:
        return "Even"
    return "Odd"

def display_result(numbers):
    for number in numbers:
        result = check_number(number)
        print(number, "is", result)

numbers = [10, 15, 20, 25, 30]
display_result(numbers)
print("Checking completed")