import os

print("============================================================\n==================Calculator With History===================\n============================================================")
# 1. & 2. START the program and DEFINE the name of the history file
history_file = "history.txt"

# 3. LOOP forever
while True:
    # a. ASK the user for a calculation or a command
    print("\nCommands: 'history', 'clear', 'exit' | Or enter a calculation (e.g., 8 + 5)")
    user_input = input("Enter choice: ").strip().lower()

    # b. IF user enters "exit"
    if user_input == "exit":
        print("Goodbye!")
        break

    # c. IF user enters "history"
    elif user_input == "history":
        try:
            # i. & ii. TRY to open and PRINT each line if file exists/not empty
            if os.path.exists(history_file) and os.path.getsize(history_file) > 0:
                print("\n--- Calculation History ---")
                with open(history_file, "r") as file:
                    print(file.read().strip())
            else:
                # iii. IF file doesn't exist or is empty
                print("No history found.")
        except Exception as e:
            print(f"Error reading history: {e}")
        
        # iv. CONTINUE to the next loop
        continue

    # d. IF user enters "clear"
    elif user_input == "clear":
        # i. OPEN and overwrite with nothing
        with open(history_file, "w") as file:
            pass
        # ii. & iii. PRINT message and CONTINUE
        print("History cleared.")
        continue

    # e. OTHERWISE (assume user entered a calculation)
    else:
        try:
            # i. TRY to parse the input
            parts = user_input.split()
            
            # ii. IF input is not valid (must be: number operator number)
            if len(parts) != 3:
                print("Invalid input. Please use format: number operator number (e.g., 8 + 5)")
                continue

            num1 = float(parts[0])
            operator = parts[1]
            num2 = float(parts[2])

            # iii. PERFORM the calculation
            result = None
            if operator == "+":
                result = num1 + num2
            elif operator == "-":
                result = num1 - num2
            elif operator == "*":
                result = num1 * num2
            elif operator == "/":
                # Check for divide by zero
                if num2 == 0:
                    print("Error: Cannot divide by zero.")
                    continue
                result = num1 / num2
            else:
                print("Invalid operator. Use +, -, *, or /.")
                continue

            # iv. SHOW the result
            output = f"{num1} {operator} {num2} = {result}"
            print(f"Result: {output}")

            # v. WRITE the calculation to history
            with open(history_file, "a") as file:
                file.write(output + "\n")

        except ValueError:
            print("Invalid input. Please ensure you are entering numbers.")
            continue

# 4. END the program (occurs after break)
