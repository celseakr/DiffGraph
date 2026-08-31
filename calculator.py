# Core calculation component module
def add_numbers(a: int, b: int):
    return a + b

def divide_numbers(numerator: int, denominator: int):
    if denominator == 0:
        raise ValueError("Cannot divide by zero!")
    return numerator / denominator
