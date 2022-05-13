from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import keyboard
import pandas as pd
import openpyxl

# Initialize Selenium
ser = Service("C:\\Program Files (x86)\chromedriver.exe")
op = webdriver.ChromeOptions()
browser = webdriver.Chrome(service=ser, options=op)

# Enter guess
def enter_guess(equation):
    for character in equation:
        if character.isnumeric():
            input_el = browser.find_elements(By.XPATH, "//button[text()='" + character + "']")
            input_el[len(input_el) - 1].click()
        else:
            if character == "+":
                input_el = browser.find_elements(By.ID, "plustitle")
            elif character == "-":
                input_el = browser.find_elements(By.ID, "minustitle")
            elif character == "*":
                input_el = browser.find_elements(By.ID, "timestitle")
            elif character == "/":
                input_el = browser.find_elements(By.ID, "divtitle")
            elif character == "=":
                input_el = browser.find_elements(By.ID, "equalstitle")
            input_el[len(input_el) - 1].find_element(By.XPATH,'..').find_element(By.XPATH,'..').click()
    keyboard.press_and_release('enter')

# Evaluate guess
def evaluate_guess(guess_number):
    evaluation = []
    tiles = browser.find_elements(By.XPATH, "//div[contains(@class, 'border-solid border-2 flex')]")
    for i in range(guess_number * 8, (guess_number * 8) + 8):
        if "#398874" in tiles[i].get_attribute('class'):
            evaluation.append(2)
        elif "#820458" in tiles[i].get_attribute('class'):
            evaluation.append(1)
        else:
            evaluation.append(0)
    return evaluation

# Trim down potential solutions
def trim_list_of_guesses(potential_equations, selected_equation, evaluation):
    for i in range(6):
        if evaluation[i] == 0:
            remove = True
            occurrences = find(selected_equation, selected_equation[i])
            occurrences.remove(i)
            if len(occurrences) > 0:
                for occurrence in occurrences:
                    if evaluation[occurrence] == 1 or evaluation[occurrence] == 2:
                        remove = False
            if remove:
                for equation in list(potential_equations):
                    if selected_equation[i] in equation:
                        potential_equations.remove(equation)
        elif evaluation[i] == 1:
            for equation in list(potential_equations):
                if selected_equation[i] not in equation or selected_equation[i] == equation[i]:
                    potential_equations.remove(equation)
        else:
            for equation in list(potential_equations):
                if selected_equation[i] != equation[i]:
                    potential_equations.remove(equation)
    return potential_equations

# Return list of occurrences of a character in a string
def find(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]

# Solve Nerdle
def unnerdle():
    # Set up Selenium browser
    browser.get("https://www.nerdle.com")

    # Start program when escape key is pressed
    keyboard.wait('esc')
    print("Running...")

    # Import potential equations
    dfs = pd.read_excel("potential_equations.xlsx", engine="openpyxl")
    potential_equations = dfs['equation'].values.tolist()

    # Initialize counters
    guess_number = 0

    # Iterate for six attempts
    while guess_number < 6:

        # Enter guess
        if len(potential_equations) > 0:
            equation = potential_equations[0]
            enter_guess(equation)
        else:
            print("Error: Ran out of options!")
            return

        # Evaluate guess
        evaluation = evaluate_guess(guess_number)

        # Check if Nerdle has been solved
        if sum(evaluation) == 16:
            print("Solved in {} attempts!".format(guess_number + 1))
            return

        # Trim down potential solutions
        potential_equations = trim_list_of_guesses(potential_equations, equation, evaluation)
        if equation in potential_equations:
            potential_equations.remove(equation)

        # Increment guess number
        guess_number = guess_number + 1

    # Admit failure
    if guess_number == 6:
        print("Could not guess in six attempts!")

if __name__ == '__main__':
    unnerdle()