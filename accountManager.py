# PROGRAM TO MAINTAIN AN ACCOUNT OF PASSWORDS
# PASSWORDS WILL BE ENCRYPTED AND STORED IN AN SQLITE3 DATABASE
# USER WILL BE ABLE TO ADD, REMOVE, MODIFY, AND SEARCH FOR ACCOUNTS INFORMATION

# TO DO LIST:
#   ADD SUPPORT FOR A GUI INSTEAD OF CLI
#   ADD SUPPORT FOR MULTIPLE USERS
import os
import sys
import sqlite3
import csv

from encryption import encrypt 
from randPassGenFunction import randPassGen
from passwords import PasswordAccess, genPass
from menu import menu
from database import AccountDatabase


# **********************************************************************
# CHANGE THESE SIX GLOBAL VARIABLES TO ALLOW FOR PORTABILITY AND SECURITY
# CREATE A DATABASE TO CONTAIN USER INFORMATION (LOGIN NAME, PASSWORD)...as
# A SEPARATE DATABASE WILL BE CREATED FOR EACH USER TO STORE INFORMATION
# WILL ALLOW FOR MULTIPLE USERS TO LOGIN AND ACCESS THE INFORMATION
# ALLOW THE USER TO CREATE NEW USERS, DELETE USERS, CHANGE PASSWORDS, CHANGE BACKUP LOCATION...
# **********************************************************************

# VARIABLES FOR FILE PATHS AND REQUIRED PROGRAM INFORMATION
filesDir = 'F:\\myprograms\\python27\\accountmanagerV2\\files\\'

# CHARACTERS USED FOR ENCRYPTION
# these are the characters that the password was created using
EncryptChars = "A2HQuNq{XEgo/PwhLt)BI=a6cz43*VkSDl`KxU%F.Y\~\"p?!;j>dGrOZ}<T0$v,n-ye5Wm]i^7&:('9M[8+J|fb@Rs_C#1"

# HOW FAR TO SHIFT EACH CHARACTER DURING ENCRYPTION
# password was created with encryption shift of 6
EncryptShift = 6

# READS THE MASTER PASSWORD FOR ACCESS TO THE PROGRAM
g = open((filesDir + 'masterPassword.txt'), 'r')
masterPass = encrypt(g.read(), EncryptChars, -EncryptShift, reservedSymbols='')
g.close()

# DIRECTORY OF THE FILE WHERE THE DATABASE OF ACCOUNTS IS KEPT
g = open((filesDir + 'databaseDirectory.txt'), 'r')
databaseDirectory = g.read() + '\\accounts.db'
g.close()

# DIRECTORY OF THE BACKUP FILE
g = open((filesDir + 'backupLocation.txt'), 'r')  # path of the file containing location of the backupFile
backupFile = g.read()
g.close()


# PROTECTED PASSWORD ACCESS
access = PasswordAccess(masterPass, maxTries=3, attempts=0)

# INITIALIZE THE ACTION FOR THE MAIN WHILE LOOP IN THE BODY
action = ""
if access:
    # CONNECTS TO DATABASE
    Database1 = AccountDatabase("accountsDB", databaseDirectory, backupFile, EncryptChars, EncryptShift)
    action = "enter"
# EXITS THE PROGRAM IF THE USER DOES NOT GUESS THE PASSWORD CORRECTLY
else:
    exitOnEnter = raw_input('nice try....')
    action = "exit"


# INITIALIZATIONS FOR THE MAIN PROGRAM LOOP
options = ['search', 'modify', 'create', 'delete', 'backup', 'help', 'exit']
history = []
# MAIN LOOP FOR PROGRAM - ALLOWS USER TO READ, MODIFY, DELETE, BACKUP, ETC... ON ACCOUNTS
while action != 'exit':

    # DISPLAYS A MENU OF OPTIONS AND GATHERS USER INPUT
    action = menu(options).lower()
    history.append(action)

    # ************************************************
    # INCLUDE AN OPTION TO GET THE ACCOUNTS WITH TASKS
    # ************************************************

    # QUERY DATABASE FOR A SEARCH TERM
    if action == '1' or action == 'search':
        found = Database1.search()
        Database1.displayAccount(found)

    # MODIFY AN EXISTING ACCOUNT IN THE DATABASE
    elif action == '2' or action == 'modify':
        # FIND THE ACCOUNT WE WANT TO MODIFY
        accountToUpdate = Database1.search("Account to modify: ")
        confirmModify = raw_input("Are you sure you want to modify '%s'? " % Database1.decode(accountToUpdate)).lower()
        if accountToUpdate != "" and confirmModify == "y" or confirmModify == "yes":
            Database1.modify(accountToUpdate)

    # CREATE A NEW ACCOUNT AND ADD IT TO THE DATABASE
    elif action == '3' or action == 'create':
        Database1.insert()

    # DELETES AN ACCOUNT BASED ON NAME
    elif action == '4' or action == 'delete':
        accountToDelete = Database1.search(prompt="account to delete: ")
        confirmDelete = raw_input("Are you sure you want to delete '%s'?" % Database1.decode(accountToDelete)).lower()
        if accountToDelete != "" and (confirmDelete == "y" or confirmDelete == "yes"):
            Database1.remove(accountToDelete)
        else:
            print("'%s' not deleted" % accountToDelete)

    elif action == '5' or action == 'backup':
        Database1.backup()

    # DISPLAYS THE HELP MESSAGE FOR THE PROGRAM
    elif action == '6' or action == 'help':
        os.system('cls')
        g = open(filesDir + 'help.txt', 'r')
        helpMessage = g.read()
        g.close()
        print(helpMessage)
        closeHelp = raw_input("")

    # EXITS THE PROGRAM
    elif action == '7' or action == 'exit' or action == 'quit':
        action = 'exit'
         
    else:
        os.system('cls')
        print('did not recognize: \'%s\'' % action)


# CLOSE DATABASE
Database1.db.close()
