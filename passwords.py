import getpass
import random
import string
from menu import menu

def PasswordAccess(password, maxTries=3, attempts=0):
    """Determines if user enters correct password. Takes the password as input and the maximum number of tries
        returns true or false depending on if the user guess the password
        @param password (string) - password to test passwords attempts against
        @param maxTries (int) - the maximum number of times the user can attempt to guess password
        @param attempts (int) - the current number of tries
        @return (bool) - True if user can get access, False otherwise
    """

    access = False
    while attempts < maxTries and not access:

        attempt = getpass.getpass("password: ")
        # attempt = raw_input("password: ")

        if attempt == password:
            access = True
        else:
            access = False
        attempts += 1
    return access


def randPassGen(length=8, characters=(string.ascii_letters + string.digits)):
    """generates a random password from a string of possible characters
        @param length (int) - the length of the password
        @param characters (string) - characters that can be included in password
        @return (string) - randomly generated password
    """

    passwordArray = []

    # POPULATES THE PASSWORD ARRAY WITH CHARACTERS
    for i in range(0, length):
        passwordArray.append(random.choice(characters))

    # CONVERT PASSWORD ARRAY FROM ARRAY TO STRING
    passwordString = ''.join(passwordArray)

    return passwordString


def genPass():
        """creates a password, user generated or random loops until user confirms the previously entered password"""

        usePass = False
        password = ''

        # LOOPS UNTIL USER HAS NOT CONSENTED TO PASSWORD
        while not usePass:

            # ARRAY CONTAINING THE TYPES OF PASSWORD GENERATION, IN ADDITION TO USER GENERATED
            passTypes = ['random']  # add any other types of password generation to the array

            # DISPLAYS A MENU FOR THE USER TO CHOOSE WHAT TYPE OF PASSWORD GENERATION TO USE
            passType = menu(passTypes, whatToDo='password: type password to use your own, otherwise select an option',
                            clearScreenBefore=False, clearScreenAfter=False)

            # USER WANTS A RANDOM PASSWORD
            if str(passType) == '1' or passType.lower() == 'random':
                lengthOfPass = int(raw_input('length of password: '))
                password = randPassGen(length=lengthOfPass)

                # CHECK TO MAKE SURE THE USER WANTS TO USE THE PASSWORD
                use = (raw_input('use \'%s\'? (y/n) ' % password)).lower()
                if use == 'y' or use == 'yes':
                    usePass = True
                else:
                    usePass = False

            # USER ENTERED THEIR OWN PASSWORD
            else:
                password = passType
                usePass = True

        return password
