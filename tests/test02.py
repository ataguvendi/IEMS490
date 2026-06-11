import json, os

FILE = "history.json"


def add(a: float, b: float) -> float:
	'''
	Returns the sum of two numbers.

	Parameters:
		a: The first operand.
		b: The second operand.

	Returns: The result of adding a and b.
	'''
	return a + b


def subtract(a: float, b: float) -> float:
	'''
	Returns the difference of two numbers.

	Parameters:
		a: The first operand (minuend).
		b: The second operand (subtrahend).

	Returns: The result of subtracting b from a.
	'''
	return a - b


def multiply(a: float, b: float) -> float:
	'''
	Returns the product of two numbers.

	Parameters:
		a: The first operand.
		b: The second operand.

	Returns: The result of multiplying a and b.
	'''
	return a * b


def divide(a: float, b: float) -> float | None:
	'''
	Returns the quotient of two numbers, or None if division by zero is attempted.

	Parameters:
		a: The dividend.
		b: The divisor.

	Returns: The result of dividing a by b, or None if b is zero.
	'''

	if b == 0:
		return None
	return a / b


def load() -> list:
	'''
	Loads the calculation history from the JSON file on disk.

	Returns: A list of history entry strings, or an empty list if no file exists.
	'''

	if not os.path.exists(FILE):
		return []

	with open(FILE) as f:
		return json.load(f)


def save(h: list, a: float, op: str, b: float, r: float) -> None:
	'''
	Appends a new calculation entry to the history list and writes it to disk.

	Parameters:
		h:  The current history list to append to.
		a:  The first operand used in the calculation.
		op: The operator symbol used in the calculation.
		b:  The second operand used in the calculation.
		r:  The result of the calculation.

	Returns: None
	'''
	h.append(f"{a} {op} {b} = {r}")

	with open(FILE, "w") as f:
		json.dump(h, f)


def print_result(a: float, op: str, b: float, r: float) -> None:
	'''
	Prints a formatted string showing the full calculation and its result.

	Parameters:
		a:  The first operand used in the calculation.
		op: The operator symbol used in the calculation.
		b:  The second operand used in the calculation.
		r:  The result of the calculation.

	Returns: None
	'''
	print(f"\n{a} {op} {b} = {r}\n")


def print_history(h: list) -> None:
	'''
	Prints all past calculation entries stored in the history list.

	Parameters:
		h: The history list of calculation entry strings to display.

	Returns: None
	'''

	if not h:
		print("no history")
		return

	print("\n--- history ---")

	for entry in h:
		print(entry)

	print("---------------\n")


def run() -> None:
	'''
	Runs the main interactive calculator loop, prompting the user for input,
	performing calculations, displaying results, and saving history.

	Returns: None
	'''
	h = load()

	while True:
		a = float(input("first number: "))
		op = input("operator (+/-/*/÷): ").strip()
		b = float(input("second number: "))

		if op == "+":
			r = add(a, b)
		elif op == "-":
			r = subtract(a, b)
		elif op == "*":
			r = multiply(a, b)
		elif op == "÷":
			r = divide(a, b)

			if r is None:
				print("cant divide by zero")
				continue
		else:
			print("unknown operator")
			continue

		print_result(
			a, #comment
			op,
			b,
			r
		)
		save(
			h,
			a,
			op,
			b,
			r
		)

		again = input("again? (y/n): ").strip().lower()

		if again != "y":
			print_history(h)
			break


run()
