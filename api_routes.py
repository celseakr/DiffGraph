from calculator import add_numbers, divide_numbers

# Public facing interface layer
def handle_addition_request(payload):
    # Relies on the exact contract signature of add_numbers(a, b)
    return add_numbers(payload["num1"], payload["num2"])

def handle_division_request(payload):
    return divide_numbers(payload["x"], payload["y"])
