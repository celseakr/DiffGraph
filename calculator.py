# Modified calculation engine - CHANGED ARGUMENT NAMES!
def add_numbers(number1: int, number2: int):
    return number1 + number2

def divide_numbers(numerator: int, denominator: int):
    if denominator == 0:
        raise ValueError("Cannot divide by zero!")
    return numerator / denominator
