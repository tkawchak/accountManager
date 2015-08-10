# ACCOUNT MANAGER:
# PROGRAM THAT ALLOWS MULTIPLE USERS TO STORE INFORMATION ABOUT ACCOUNTS (PASSWORDS, LOGIN CREDENTIALS, ETC...)
# EACH USER WILL HAVE TO SET UP A PASSWORD AND FILE LOCATIONS TO START
# EACH USER WILL THEN BE ABLE TO CREATE, MODIFY, SEARCH, DELETE, BACKUP (TO A .CSV) ALL OF THE ACCOUNTS
# ACCOUNTS ARE ENCRYPTED AND THEN STORED IN THE DATABASE, AND THEN DECRYPTED WHEN RETRIEVED FROM THE DATABASE

# TO DO LIST:
#   MAKE SURE THIS WORKS CROSS PLATFORM.  DESIGNED ON WINDOWS, WILL TEST ON LINUX
#   ADD SUPPORT FOR A GUI INSTEAD OF CLI
#   ALLOW USERS TO MODIFY THE ACCOUNT SETTINGS FROM THE MAIN MENU OF PROGRAM
#   INCLUDE AN OPTION TO START THE WEBSITE OF AN ACCOUNT THAT WAS SEARCHED FOR
#   INCLUDE AN OPTION TO COPY THE PASSWORD OF THE ACCOUNT TO THE CLIPBOARD
#   FIGURE OUT HOW TO SECURELY ALLOW REMOTE ACCESS, EITHER PUT ON A WEBSITE OR THROUGH A REMOTE CONNECTION

import os
import sys
import sqlite3
import csv

from encryption import encrypt, fix_filepath
from passwords import PasswordAccess, genPass, randPassGen
from menu import menu
from database import AccountDatabase

# *********************************************************************************
# CHANGE THESE TO YOUR LIKING IF YOU ARE GOING TO SET UP ACCOUNTS USING THE PROGRAM
# *********************************************************************************
# CHARACTERS USED FOR ENCRYPTION
EncryptChars = "A2HQuNq{XEgo/PwhLt)BI=a6cz43*VkSDl`KxU%F.Y\\~\"p ?!;j>dGrOZ}<T0$v,n-ye5Wm]i^7&:('9M[8+J|fb@Rs_C#1"
# HOW FAR TO SHIFT EACH CHARACTER DURING ENCRYPTION
EncryptShift = 10


# PASSWORD ACCESS TO SYSTEM WITH MULTIPLE USER SUPPORT
userDB = sqlite3.connect("users.db")
userData = userDB.cursor()
userData.execute("CREATE TABLE IF NOT EXISTS users"
                 "(ID INTEGER PRIMARY KEY UNIQUE NOT NULL,"
                 "USERNAME TEXT,"
                 "PASSWORD TEXT,"
                 "DATABASE_PATH TEXT,"
                 "BACKUP_LOCATION TEXT"
                 ")")

action = "getuser"
while action == "getuser":

    # GET THE USER INPUT FOR USERNAME
    user = raw_input("username: ").lower()
    userEncrypt = encrypt(user, EncryptChars, EncryptShift, "")

    # SELECT THE INFORMATION FOR THAT USER
    userData.execute("SELECT USERNAME, PASSWORD, DATABASE_PATH, BACKUP_LOCATION "
                     "FROM users WHERE USERNAME=?", (userEncrypt,))
    row = userData.fetchone()

    # USER CHOSE THE QUIT APPLICATION
    if user == "" or user == "exit" or user == "quit" or user == "leave":
        action = "login failed"

    # ASKS THE USER TO CREATE AN ACCOUNT IF THE USERNAME DOES NOT MATCH ANY
    elif row is None:
        createUser = raw_input("No username matched.  Create user '%s'? (y/n): " % user).lower()
        if createUser == "y" or createUser == "yes":
            print("Please enter some information below. All file paths should not contain file names.")
            password = raw_input("password: ")
            passwordEncrypt = encrypt(password, EncryptChars, EncryptShift, "")
            databasePath = raw_input("Data base path: ")
            databasePathEncrypt = encrypt(databasePath, EncryptChars, EncryptShift, "")
            while not os.path.isdir(databasePath):
                print("'%s' is not a working directory on you computer." % databasePath)
                databasePath = raw_input("Data base folder: ")
                databasePathEncrypt = encrypt(databasePath, EncryptChars, EncryptShift, "")
            backupPath = raw_input("Account backup folder: ")
            backupPathEncrypt = encrypt(backupPath, EncryptChars, EncryptShift, "")
            while not os.path.isdir(backupPath):
                print("'%s' is not a working directory on you computer." % backupPath)
                backupPath = raw_input("Data base path: ")
                backupPath = encrypt(backupPath, EncryptChars, EncryptShift, "")
            userData.execute("INSERT INTO users (USERNAME, PASSWORD, DATABASE_PATH, BACKUP_LOCATION)"
                             "VALUES (?,?,?,?)", (userEncrypt, passwordEncrypt, databasePathEncrypt, backupPathEncrypt))
            userDB.commit()

            wait = raw_input("Thanks for registering.  Please press enter and then login at the main screen.")

        os.system('cls' if os.name == 'nt' else 'clear')
        action = "getuser"

    # GETS THE PASSWORD FOR THE USER AND ATTEMPTS TO GET INTO ACCOUNT
    else:
        # GET THE INFORMATION FROM THE USERS DATABASE AND DECRYPT IT
        user = encrypt(row[0], EncryptChars, -EncryptShift, "")
        password = encrypt(row[1], EncryptChars, -EncryptShift, "")
        databasePath = encrypt(row[2], EncryptChars, -EncryptShift, "")
        backupPath = encrypt(row[3], EncryptChars, -EncryptShift, "")

        # ALLOWS USER TO ATTEMPT TO ENTER CORRECT PASSWORD
        access = PasswordAccess(password, maxTries=3, attempts=0)
        if access:
            # CONNECT TO THE USERS DB
            databaseFile = fix_filepath(databasePath + ("/%s.db" % user))
            backupFile = fix_filepath(backupPath + ("/%sAccountBackup.csv" % user))
            Database1 = AccountDatabase(user, databaseFile, backupFile, EncryptChars, EncryptShift)
            action = "enter"
        else:
            action = "login failed"

        os.system('cls' if os.name == 'nt' else 'clear')


# INITIALIZATIONS FOR THE MAIN PROGRAM LOOP
options = ['Search Accounts', 'Modify Account', 'Create Account', 'Show Uncompleted Tasks', 'Delete An Account',
           'Backup All Accounts', 'Help', 'Quit']

# MAIN LOOP FOR PROGRAM - ALLOWS USER TO READ, MODIFY, DELETE, BACKUP, ETC... ON ACCOUNTS
while action != "exit" and action != "login failed":

    # DISPLAYS A MENU OF OPTIONS AND GATHERS USER INPUT
    action = menu(options).lower()

    # *******************************************************
    # INCLUDE OPTION HERE FOR USER TO CHANGE ACCOUNT SETTINGS
    # INCLUDE OPTION HERE TO SEE ACCOUNTS WHOSE PASSWORDS HAVE NOT BEEN CHANGED RECENTLY
    # *******************************************************

    # QUERY DATABASE FOR A SEARCH TERM
    if action == '1':
        found = Database1.search()
        Database1.displayAccount(found)

        wait = raw_input("")

    # MODIFY AN EXISTING ACCOUNT IN THE DATABASE
    elif action == '2':
        # FIND THE ACCOUNT WE WANT TO MODIFY
        accountToUpdate = Database1.search("Account to modify: ")
        confirmModify = raw_input("Are you sure you want to modify '%s'? " % Database1.decode(accountToUpdate)).lower()
        if accountToUpdate != "" and confirmModify == "y" or confirmModify == "yes":
            Database1.modify(accountToUpdate)
        wait = raw_input("")

    # CREATE A NEW ACCOUNT AND ADD IT TO THE DATABASE
    elif action == '3':
        Database1.insert()

    # SHOWS THE ACCOUNTS THAT HAVE TASKS PENDING
    elif action == '4':
        Database1.get_tasks()
        wait = raw_input("")

    # DELETES AN ACCOUNT BASED ON NAME
    elif action == '5':
        accountToDelete = Database1.search(prompt="account to delete: ")
        confirmDelete = raw_input("Are you sure you want to delete '%s'?" % Database1.decode(accountToDelete)).lower()
        if accountToDelete != "" and (confirmDelete == "y" or confirmDelete == "yes"):
            Database1.remove(accountToDelete)
        else:
            print("'%s' not deleted" % accountToDelete)
        wait = raw_input("")

    # BACKUP THE ACCOUNTS FOR THE USER TO THE BACKUP FILE
    elif action == '6':
        Database1.backup()

    # DISPLAYS THE HELP MESSAGE FOR THE PROGRAM
    elif action == '7':
        os.system('cls' if os.name == 'nt' else 'clear')
        g = open('help.txt', 'r')
        helpMessage = g.read()
        g.close()
        print(helpMessage)
        wait = raw_input("")

    # EXITS THE PROGRAM
    elif action == '8':
        action = 'exit'

    # THE USER INPUT WAS NOT RECOGNIZED, GO BACK TO MAIN MENU
    else:
        os.system('cls' if os.name == 'nt' else 'clear')
        print('did not recognize: \'%s\'' % action)


# CLOSE DATABASE, AS LONG AS IT WAS OPENED
if action == "exit":
    Database1.db.close()
