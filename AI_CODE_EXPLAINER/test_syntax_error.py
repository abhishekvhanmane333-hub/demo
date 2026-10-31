def add(a, b)
    return a + b

print(add(10, 20))



display_bill(500, 3)
print("Bill Generated")

# 02 Indentation Error
def check_marks(marks):
    if marks >= 35:
        print("Pass")
    else:
    print("Fail")

def show_result(name, marks):
    print("Student:", name)
    check_marks(marks)

show_result("Rahul", 28)

# 03 Name Error
def calculate_salary(basic, bonus):
    total_salary = basic + bonus
    return total_salary

def show_salary(name, basic, bonus):
    salary = calculate_salary(basic, bonus)
    print("Employee:", name)
    print("Salary:", salary)

employee_name = "Amit"
basic_salary = 25000
bonus_amount = 3000

show_salary(employee_name, basic_salary, bonus_amount)
print("Department:", department)

