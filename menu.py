import os


def menu(options, whatToDo="Enter the number of the corresponding option.", clearScreenBefore = True, clearScreenAfter = True):
    """basic menu for cmd line menu text.
        @param options (string[]) - array of all options for the menu
        @param whatToDo (string) - prompt for the menu
        @param clearScreenBefore (bool) - if True, screen is cleared before menu is displayed
        @param clearScreenAfter (bool) - if True, screen is cleared after user input is read from menu choice
        @return (string) - user choice for menu
    """

    if clearScreenBefore:
        os.system('cls' if os.name == 'nt' else 'clear')

    # DISPLAYS THE MENU OPTIONS
    print(whatToDo)
    for option in range(0, len(options)):
        print("\t%d) %s" % ((option + 1), options[option]))

    # GETS THE USER INPUT FROM THE MENU
    action = raw_input("\n> ")

    if clearScreenAfter:
        os.system('cls' if os.name == 'nt' else 'clear')

    return action
