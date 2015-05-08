import sqlite3
import os
import csv
from encryption import encrypt


class AccountDatabase:
    """class to contain a database and relevant function"""

    def __init__(self, dbName, dbFile, backupFile, encryptChars, encryptShift, reservedSymbols=""):
        """initializes an account database with certain information
            @param dbName (string) - name to use for database
            @param dbFile (string) - file path of the database
            @param backupFile (string) - file path of the backup file
            @param encryptChars (string) - characters used in encryption
            @param encryptShift (int) - amount of shift to be applied for encryption
            @param reservedSymbols (string) - symbols that are not changed during encryption
        """

        self.dbFile = dbFile
        self.dbName = dbName
        self.tableName = "accounts"
        self.backupFile = backupFile
        self.encryptChars = encryptChars
        self.encryptShift = encryptShift
        self.reservedSymbols = reservedSymbols

        # CONNECTS TO THE DATABASE
        self.dataBase = sqlite3.connect(self.dbFile)
        self.db = self.dataBase.cursor()

        # **********************************************************
        # THINK ABOUT THE CATEGORIES THAT ARE NEEDED FOR THE ACCOUNTS
        # DO WE WANT TO INCLUDE CATEGORIES LIKE PRODUCT_KEY OR CATEGORY
        # ***********************************************************

        # CREATES A TABLE WITH THE FOLLOWING PROPERTIES IF IT DOES NOT ALREADY EXIST
        self.db.execute("CREATE TABLE IF NOT EXISTS accounts"
                        "("
                        "ID INTEGER PRIMARY KEY UNIQUE NOT NULL,"  # id number for accounts
                        "NAME TEXT UNIQUE NOT NULL,"  # name of account
                        "WEBSITE TEXT,"  # website of accounts (something.com)
                        "EMAIL TEXT,"  # email of accounts (someone@something.com), encrypted
                        "USERNAME TEXT,"  # encrypted
                        "PASSWORD TEXT,"  # encrypted
                        "MORE TEXT,"  # more information about the account, encrypted
                        "TAGS TEXT,"  # identifiers for searching
                        "DATEMODIFIED DEFAULT CURRENT_DATE"  # updated whenever the entry is modified
                        ")")

        # COMMITS CHANGES TO THE DATABASE SO THEY ARE SAVED
        self.dataBase.commit()

    def encode(self, info):
        """easier implementation of the encryption function
            @param info (string) - the information to be encrypted
            @return (string) - the encrypted version of info
        """

        newInfo = encrypt(info, self.encryptChars, self.encryptShift, reservedSymbols=self.reservedSymbols)
        return newInfo

    def decode(self, info):
        """simple implementation of encoder to decode string previously encoded with it
            @param info (string) - the information to be decoded
            @return (string) - the information that was decoded
        """

        newInfo = encrypt(info, self.encryptChars, -self.encryptShift, reservedSymbols=self.reservedSymbols)
        return newInfo

    def search(self, prompt="Search for: "):
        """searches the database for the target.  Searches the name, category, website, tags.
            Prompts the user for the search term.
            recursively display the results of the search until the search has one match
            @param prompt (string) - text to prompt for search
            @return (string) the name of the account that we searched for
        """

        matches = {}  # name of search matches
        matchCount = 0  # number of search matches

        # RECURSIVELY SEARCH THE DATABASE FOR A TERM
        target = raw_input(prompt)  # contains the name of the account to return from the search

        # **********************************************************************
        # ENCRYPT THE SEARCH TERM SO THAT WE DON'T HAVE TO DECRYPT EACH CATEGORY
        # **********************************************************************

        # SELECT ONLY THE BASIC CATEGORIES TO SEARCH
        self.db.execute("SELECT NAME, WEBSITE, TAGS FROM accounts")

        row = self.db.fetchone()
        while not row == None:

            for category in row:
                if target in category:
                    matches[matchCount] = row[0]  # appends the name of the account to the search results
                    matchCount += 1  # UPDATE THE COUNT IF WE HAVE A MATCH
                    break

            # FETCH THE NEXT ROW
            row = self.db.fetchone()

        # **************************************************
        # SOMEHOW ALLOW THE USER TO LIST ALL OF THE ACCOUNTS
        # MAYBE IF THE USER ENTERS "all"
        # **************************************************

        # DECIDE WHAT VALUE TO RETURN
        if matchCount == 1:
            return matches[0]

        elif target == "":
            return ""

        elif matchCount > 1:
            print("%d search results for '%s':" % (matchCount, target))
            # PRINTS OUT THE MATCHES FOR THE SEARCH TERM
            for account in range(0, matchCount):
                print("%d) %s" % (account + 1, matches[account]))

            account = int(raw_input("\nNumber of correct account or just press enter to search again: "))
            print(account, matchCount)
            if 1 <= account <= matchCount:
                return matches[account - 1]
            else:
                return self.search(prompt=prompt)

        else:
            return self.search(prompt=("No matches for search '%s'.\nSearch for: " % target))

    def modify(self, name):
        """modifies an account based upon the target term.
            Prompts the user for the account to change and the new info
            @return (string) - name of the account that was just changed
        """

        self.displayAccount(name)

        # ****************************************************************
        # SET THIS SO THAT IF THE USER ENTERS '' THEN THE OLD INPUT IS KEPT
        # WILL HAVE TO READ THE DATA FROM THE OLD ACCOUNT FIRST
        # ****************************************************************
        print("Please enter new information information for '%s'." % name)
        newName = raw_input("Name: ")
        website = raw_input("Website: ")
        email = raw_input("Email: ")
        username = raw_input("Username: ")
        password = raw_input("Password: ")
        moreInfo = raw_input("More Info: ")
        tags = raw_input("Tags: ")

        # ***********************************************
        # INFORMATION WILL HAVE TO BE ENCRYPTED EVENTUALLY
        # ************************************************
        self.db.execute("UPDATE accounts SET NAME = ?, WEBSITE = ?, EMAIL = ?, USERNAME = ?, PASSWORD = ?, MORE = ?, TAGS = ?, DATEMODIFIED = CURRENT_DATE WHERE NAME = ?",
                        (newName, website, email, username, password, moreInfo, tags, name))

        self.dataBase.commit()
        return name

    def insert(self):
        """inserts a new account into the database, prompts user for details
            @return (string) - name of the account that was just inserted
        """

        print("Please enter some information about the account.")
        name = raw_input("Name: ")
        website = raw_input("Website: ")
        email = raw_input("Email: ")
        username = raw_input("Username: ")
        # *****************************************
        # ADD ABILITY TO SUPPORT A RANDOM PASSWORD
        # MAYBE HAVE THE USER JUST ENTER "random"
        # LET THE USER CHOOSE WHAT KIND OF CHARACTERS WILL BE IN RANDOM PASSWORDS
        # *****************************************
        password = raw_input("Password: ")
        moreInfo = raw_input("More Info: ")
        tags = raw_input("Tags: ")

        # INSERT THE INFORMATION
        # **************************************
        # CHECK TO SEE IF THE NAME ALREADY EXISTS
        # ENCRYPT THE INFORMATION BEFORE INSERTING
        # ***************************************
        self.db.execute("INSERT INTO accounts (NAME, WEBSITE, EMAIL, USERNAME, PASSWORD, MORE, TAGS) VALUES (?,?,?,?,?,?,?)",
                        (name, website, email, username, password, moreInfo, tags))

        self.dataBase.commit()
        return name

    def remove(self, name):
        """removes the account with the matching target
            @param name (string) - name of the account to be deleted. Assumed to already be in table
        """

        self.db.execute("DELETE FROM accounts WHERE NAME = ?", (name,))
        print("'%s' deleted" % name)
        self.dataBase.commit()

    def backup(self):
        """performs a backup of the database to the backup file .csv"""
        # ***************************************
        # MODIFY THIS AFTER PROGRAM IS WORKING
        # ***************************************

    def displayAccount(self, name):
        """displays the desired information from the account
            @param name (string) - the name of the account to be displayed
        """

        # ****************************************
        # MUST DECRYPT THE INFORMATION FIRST
        # ****************************************

        if name != "":
            accountInfo = self.db.execute("SELECT NAME, WEBSITE, EMAIL, USERNAME, PASSWORD, MORE, DATEMODIFIED FROM accounts WHERE NAME = ?", (name,))

        else:
            accountInfo = ""

        # ********************************************
        # MODIFY FORMATTING
        # DISPLAY CATEGORY BEFORE INFORMATION
        # ONLY DISPLAY THE FIELDS WITH DATA
        # ********************************************
        categories = ["NAME", "WEBSITE", "EMAIL", "USERNAME", "PASSWORD", "MORE", "DATE MODIFIED"]
        for info in accountInfo:
            print(info)
