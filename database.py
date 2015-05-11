import sqlite3
import os
import csv
import datetime
from encryption import encrypt
import passwords


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
        self.categories = ["ID", "NAME", "DESCRIPTION", "EMAIL", "USERNAME", "PASSWORD", "ACCESS_CODE", "WEBSITE",
                           "MISCELLANEOUS_INFO", "PENDING_TASKS", "SEARCH_TAGS", "DATE_MODIFIED", "SEARCH_COUNT"]

        # CONNECTS TO THE DATABASE
        self.dataBase = sqlite3.connect(self.dbFile)
        self.db = self.dataBase.cursor()

        # CREATES A TABLE WITH THE FOLLOWING PROPERTIES IF IT DOES NOT ALREADY EXIST
        self.db.execute("CREATE TABLE IF NOT EXISTS accounts"
                        "("
                        "ID INTEGER PRIMARY KEY UNIQUE NOT NULL,"  # id number for accounts
                        "NAME TEXT UNIQUE NOT NULL,"  # name of account
                        "DESCRIPTION TEXT,"  # a description of the account
                        "EMAIL TEXT,"  # email of accounts (someone@something.com)
                        "USERNAME TEXT,"
                        "PASSWORD TEXT,"
                        "ACCESS_CODE TEXT,"
                        "WEBSITE TEXT,"  # website of accounts (something.com)
                        "MISCELLANEOUS_INFO TEXT,"  # more information about the account
                        "PENDING_TASKS TEXT,"  # things that I want to do with this account
                        "SEARCH_TAGS TEXT,"  # identifiers for searching
                        "DATE_MODIFIED TEXT,"  # updated when the entry is modified (month, day, year)
                        "SEARCH_COUNT INTEGER"  # number of times account has been searched
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

    def get_input(self, prompt):
        """gets input for the insert function, and enrypts the info
            @param prompt(string) - prompt for the user
            @return (string) - the encoded input
        """
        value = raw_input(prompt)
        return self.encode(value)

    def get_password(self):
        """gets password input for the insert function, and allows user to generate a random password
            @param prompt (string) - the prompt for the user
            @return (string) - the password, encrypted
        """
        password = raw_input("Password: ")
        if password == "random":
            password = genPass()
        return self.encode(password)

    def updateInfo(self, newInfo, oldInfo):
        """returns the new information unless the info is "", in which case the old info is returned
            @param newInfo (string) - the new information that was entered by the user
            @param oldInfo (string) - the previously existing information
            @return (string) - the proper information
        """
        if newInfo.lower() == self.encode("same") or newInfo.lower() == self.encode("keep"):
            return oldInfo
        else:
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
        target = self.encode(raw_input(prompt))  # search target, encrypted so we don't have to decrypt each category

        self.db.execute("SELECT NAME, DESCRIPTION, SEARCH_TAGS FROM accounts")
        row = self.db.fetchone()

        # ALLOW USER TO LIST ALL ACCOUNTS BY SEARCHING "all"
        if target.lower() == self.encode("all"):
            while row is not None:
                matches[matchCount] = row[0]
                matchCount += 1

        # SEARCHES ACCOUNTS FOR THE TARGET TERM
        else:
            while row is not None:
                for category in row:
                    if target in category:
                        matches[matchCount] = row[0]  # appends the name of the account to the results
                        matchCount += 1  # updates the count when we have a match
                        break  # we already found a match in this account

                # FETCH THE NEXT ROW
                row = self.db.fetchone()

        # DECIDE WHAT VALUE TO RETURN
        if matchCount == 1:
            return matches[0]

        elif target == "":
            return ""

        elif matchCount > 1:
            print("%d search results for '%s':" % (matchCount, target))
            # PRINTS OUT THE MATCHES FOR THE SEARCH TERM
            for account in range(0, matchCount):
                print("%d) %s" % (account + 1, self.decode(matches[account])))

            account = int(raw_input("\nNumber of correct account or just press enter to search again: "))
            if 1 <= account <= matchCount:
                return matches[account - 1]
            else:
                return self.search(prompt=prompt)

        else:
            return self.search(prompt=("No matches for search '%s'.\nSearch for: " % self.decode(target)))

    def modify(self, name):
        """modifies an account based upon the target term.
            Prompts the user for the account to change and the new info
            @param name (string) - encrypted version of the name of the account to modify
            @return (string) - name of the account that was just changed
        """

        self.displayAccount(name)

        self.db.execute("SELECT NAME, DESCRIPTION, EMAIL, USERNAME, PASSWORD, ACCESS_CODE, WEBSITE,"
                        "MISCELLANEOUS_INFO, PENDING_TASKS, SEARCH_TAGS FROM accounts WHERE NAME=?", (name,))
        oldInfo = self.db.fetchone()

        # GETS THE USER INPUT FOR THE CATEGORIES TO CHANGE
        print("Please enter new information information for '%s'." % self.decode(name))
        newName = self.updateInfo(self.get_input("Name: "), oldInfo[0])
        description = self.updateInfo(self.get_input("Description: "), oldInfo[1])
        email = self.updateInfo(self.get_input("Email: "), oldInfo[2])
        username = self.updateInfo(self.get_input("Username: "), oldInfo[3])
        password = self.updateInfo(self.get_password(), oldInfo[4])
        code = self.updateInfo(self.get_input("Access Code: "), oldInfo[5])
        website = self.updateInfo(self.get_input("Website: "), oldInfo[6])
        info = self.updateInfo(self.get_input("Miscellaneous Info: "), oldInfo[7])
        tasks = self.updateInfo(self.get_input("Pending tasks: "), oldInfo[8])
        tags = self.updateInfo(self.get_input("Search tags: "), oldInfo[9])
        date = self.encode(datetime.date.today().strftime("%b %d, %Y"))

        # ACTUALLY UPDATES THE DATA
        self.db.execute("UPDATE accounts SET NAME = ?, DESCRIPTION = ?, EMAIL = ?, USERNAME = ?, PASSWORD = ?,"
                        "ACCESS_CODE = ?, WEBSITE = ?, MISCELLANEOUS_INFO = ?, PENDING_TASKS = ?, SEARCH_TAGS = ?,"
                        "DATE_MODIFIED = ? WHERE NAME = ?",
                        (newName, description, email, username, password, code, website, info, tasks, tags, date, name))

        self.dataBase.commit()
        return name

    def insert(self):
        """inserts a new account into the database, prompts user for details
            @return (string) - name of the account that was just inserted
        """

        print("Please enter some information about the account.")
        name = self.get_input("Name: ")
        description = self.get_input("Description: ")
        email = self.get_input("Email: ")
        username = self.get_input("Username: ")
        password = self.get_password()
        code = self.get_input("Access Code: ")
        website = self.get_input("Website: ")
        info = self.get_input("Misc Info: ")
        tasks = self.get_input("Pending Tasks: ")
        tags = self.get_input("Search Tags: ")
        date = self.encode(datetime.date.today().strftime("%b %d, %Y"))
        count = 0

        # CHECK TO SEE IF THE NAME ALREADY EXISTS
        # self.db.execute("SELECT NAME FROM accounts")
        # exists = False
        # while not exists:
        #     names = self.db.fetchone()
        #     if names[0] == name:
        #         exists = True

        # INSERT THE INFORMATION
        exists = False
        if not exists:
            self.db.execute("INSERT INTO accounts "
                            "(NAME, DESCRIPTION, EMAIL, USERNAME, PASSWORD, ACCESS_CODE, WEBSITE, MISCELLANEOUS_INFO, "
                            "PENDING_TASKS, SEARCH_TAGS, DATE_MODIFIED, SEARCH_COUNT) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                            (name, description, email, username, password, code, website, info, tasks, tags, date, count))

        self.dataBase.commit()
        return name

    def remove(self, name):
        """removes the account with the matching target
            @param name (string) - encrypted name of the account to be deleted. Assumed to already be in table
        """

        self.db.execute("DELETE FROM accounts WHERE NAME = ?", (name,))
        print("'%s' deleted" % self.decode(name))
        self.dataBase.commit()

    def backup(self):
        """performs a backup of the database to the backup file .csv"""
        # ***************************************
        # MODIFY THIS AFTER PROGRAM IS WORKING
        # ***************************************

    def displayAccount(self, name):
        """displays the desired information from the account
            @param name (string) - encrypted name of the account to be displayed
        """

        accountInfo = ""
        if name != "":
            self.db.execute("SELECT NAME, DESCRIPTION, EMAIL, USERNAME, PASSWORD, ACCESS_CODE, WEBSITE, "
                            "MISCELLANEOUS_INFO, PENDING_TASKS, DATE_MODIFIED "
                            "FROM accounts WHERE NAME = ?", (name,))
            accountInfo = self.db.fetchone()

        # GET THE CATEGORIES TO DISPLAY
        displayCategories = ["NAME", "DESCRIPTION", "EMAIL", "USERNAME", "PASSWORD", "ACCESS_CODE", "WEBSITE",
                             "MISCELLANEOUS_INFO", "PENDING_TASKS", "DATE_MODIFIED"]
        count = 0
        for info in accountInfo:
            if info != "":
                print("%s:\t%s" % (displayCategories[count], self.decode(info)))
            count += 1
