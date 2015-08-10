import sqlite3
import os
import csv
import datetime
from encryption import encrypt
import passwords
import locale
from functools import cmp_to_key

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
                        "ADDRESS TEXT,"  # address, not commonly used
                        "PHONE_NUMBER TEXT,"  # phone number of the account
                        "MISCELLANEOUS_INFO TEXT,"  # more information about the account
                        "PENDING_TASKS TEXT,"  # things that I want to do with this account
                        "SEARCH_TAGS TEXT,"  # identifiers for searching
                        "DATE_MODIFIED TEXT"  # updated when the entry is modified (month, day, year)
                        ");")

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
        password = passwords.genPass()
        return self.encode(password)

    def updateInfo(self, newInfo, oldInfo):
        """returns the new information unless the info is "", in which case the old info is returned
            @param newInfo (string) - the new information that was entered by the user
            @param oldInfo (string) - the previously existing information
            @return (string) - the proper information
        """

        if newInfo.lower() == self.encode("same").lower() or newInfo.lower() == self.encode("keep").lower():
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

        matches = []  # name of search matches
        decodedMatches = []
        sortedMatches = []
        matchCount = 0  # number of search matches

        # RECURSIVELY SEARCH THE DATABASE FOR A TERM
        target = self.encode(raw_input(prompt))  # search target, encrypted so we don't have to decrypt each category

        # ALLOW USER TO LIST ALL ACCOUNTS BY SEARCHING "all"
        if target.lower() == self.encode("all").lower():
            # self.db.execute("SELECT NAME, DESCRIPTION, SEARCH_TAGS FROM accounts ORDER BY NAME ASC;")
            results = self.db.execute("SELECT NAME FROM accounts ORDER BY NAME;")

        # SEARCHES ACCOUNTS FOR THE TARGET TERM
        else:
            searchTerm = "%" + target + "%"
            results = self.db.execute("SELECT NAME FROM accounts WHERE NAME LIKE ? OR DESCRIPTION LIKE ? "
                                      "OR SEARCH_TAGS LIKE ? ORDER BY NAME;", (searchTerm, searchTerm, searchTerm))

        results = self.db.fetchall()
        for row in results:
            matches.append(row[0])
            matchCount += 1

        # DECIDE WHAT VALUE TO RETURN
        if matchCount == 1:
            return matches[0]

        elif target == "":
            return ""

        elif matchCount > 1:
            print("%d search results for '%s':" % (matchCount, self.decode(target)))

            # PRINTS OUT THE MATCHES FOR THE SEARCH TERM
            decodedMatches = []
            for account in matches:
                decodedMatches.append(self.decode(account))

            # SORT THE ACCOUNTS
            sortedMatches = sorted(decodedMatches, key=str.lower)

            for account in range(0, matchCount):
                print("%d) %s" % (account + 1, sortedMatches[account]))

            account = raw_input("\nNumber of correct account or just press enter to search again: ")
            if account.isdigit() and 1 <= int(account) <= matchCount:
                return self.encode(sortedMatches[int(account) - 1])
            else:
                return self.search(prompt=prompt)

        else:
            return self.search(prompt=("No matches for search '%s'.\nSearch for: " % self.decode(target)))

    def get_tasks(self):
        """function to search the database for accounts with tasks to be completed.
            this will print out the names and pending tasks of all accounts where the task category is not blank."""

        self.db.execute("SELECT NAME, PENDING_TASKS FROM accounts;")
        row = self.db.fetchone()

        while row is not None:
            if row[1] != "":
                print("Name: %s\nTasks: %s\n" % (self.decode(row[0]), self.decode(row[1])))
            row = self.db.fetchone()

    def modify(self, name):
        """modifies an account based upon the target term.
            Prompts the user for the account to change and the new info
            @param name (string) - encrypted version of the name of the account to modify
            @return (string) - name of the account that was just changed
        """

        self.displayAccount(name)

        self.db.execute("SELECT NAME, DESCRIPTION, EMAIL, USERNAME, PASSWORD, ACCESS_CODE, WEBSITE,"
                        "ADDRESS, PHONE_NUMBER, MISCELLANEOUS_INFO, PENDING_TASKS, SEARCH_TAGS "
                        "FROM accounts WHERE NAME=?;", (name,))
        oldInfo = self.db.fetchone()

        # GETS THE USER INPUT FOR THE CATEGORIES TO CHANGE
        print("Please enter new information information for '%s'." % self.decode(name))
        newName = self.updateInfo(self.get_input("Name: "), oldInfo[0])
        description = self.updateInfo(self.get_input("Description: "), oldInfo[1])
        email = self.updateInfo(self.get_input("Email: "), oldInfo[2])
        username = self.updateInfo(self.get_input("Username: "), oldInfo[3])
        password = self.updateInfo(self.encode(passwords.genPass()), oldInfo[4])
        code = self.updateInfo(self.get_input("Access Code: "), oldInfo[5])
        website = self.updateInfo(self.get_input("Website: "), oldInfo[6])
        address = self.updateInfo(self.get_input("Address: "), oldInfo[7])
        phone = self.updateInfo(self.get_input("Phone Number: "), oldInfo[8])
        info = self.updateInfo(self.get_input("Miscellaneous Info: "), oldInfo[9])
        tasks = self.updateInfo(self.get_input("Pending tasks: "), oldInfo[10])
        tags = self.updateInfo(self.get_input("Search tags: "), oldInfo[11])
        date = self.encode(datetime.date.today().strftime("%b %d, %Y"))

        # ACTUALLY UPDATES THE DATA
        self.db.execute("UPDATE accounts SET NAME = ?, DESCRIPTION = ?, EMAIL = ?, USERNAME = ?, PASSWORD = ?,"
                        "ACCESS_CODE = ?, WEBSITE = ?, ADDRESS = ?, PHONE_NUMBER = ?, MISCELLANEOUS_INFO = ?, "
                        "PENDING_TASKS = ?, SEARCH_TAGS = ?, DATE_MODIFIED = ? WHERE NAME = ?;",
                        (newName, description, email, username, password, code, website,
                         address, phone, info, tasks, tags, date, name))

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
        address = self.get_input("Address: ")
        phone = self.get_input("Phone Number: ")
        info = self.get_input("Misc Info: ")
        tasks = self.get_input("Pending Tasks: ")
        tags = self.get_input("Search Tags: ")
        date = self.encode(datetime.date.today().strftime("%b %d, %Y"))

        # ********************************************************
        # CHECK TO SEE IF THE NAME ALREADY EXISTS BEFORE INSERTING
        # ********************************************************

        # INSERT THE INFORMATION
        exists = False
        if not exists:
            self.db.execute("INSERT INTO accounts "
                            "(NAME, DESCRIPTION, EMAIL, USERNAME, PASSWORD, ACCESS_CODE, WEBSITE, ADDRESS, PHONE_NUMBER, "
                            "MISCELLANEOUS_INFO, PENDING_TASKS, SEARCH_TAGS, DATE_MODIFIED) "
                            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?);",
                            (name, description, email, username, password, code, website,
                             address, phone, info, tasks, tags, date))

        self.dataBase.commit()
        return name

    def remove(self, name):
        """removes the account with the matching target
            @param name (string) - encrypted name of the account to be deleted. Assumed to already be in table
        """

        self.db.execute("DELETE FROM accounts WHERE NAME = ?;", (name,))
        print("'%s' deleted" % self.decode(name))
        self.dataBase.commit()

    def backup(self):
        """performs a backup of the database to the backup file .csv"""

        self.db.execute("SELECT * FROM accounts ORDER BY NAME ASC;")

        # ATTEMPTS TO DELETE BACKUP FILE INSTEAD OF ADDING TO IT
        if os.path.isdir(self.backupFile):
            os.remove(self.backupFile)

        # OPENS A .CSV FILE IN PYTHON AND WRITES TO IT
        with open(self.backupFile, 'wb') as csvfile:
            accountWriter = csv.writer(csvfile)

            newRow = ["NAME", "DESCRIPTION", "EMAIL", "USERNAME", "PASSWORD", "CODE", "WEBSITE",
                      "ADDRESS", "PHONE NUMBER", "MISCELLANEOUS INFO", "PENDING TASKS", "SEARCH TAGS", "DATE MODIFIED"]

            accountWriter.writerow(newRow)

            row = self.db.fetchone()
            while row is not None:
                newRow = []
                for column in range(1, len(row)):
                    element = self.decode(str(row[column]))
                    newRow.append(element)
                accountWriter.writerow(newRow)
                row = self.db.fetchone()

        csvfile.close()

        # THE FOLLOWING LINE OPENS THE BACKUP FILE THAT WAS JUST CREATED
        # os.system('start %s' % backupFile)

    def displayAccount(self, name):
        """displays the desired information from the account
            @param name (string) - encrypted name of the account to be displayed
        """

        # *******************************************************
        # INCLUDE OPTION HERE TO START THE WEBSITE OF THE ACCOUNT
        # INCLUDE OPTION HERE TO COPY THE PASSWORD TO CLIPBOARD
        # *******************************************************

        accountInfo = ""
        if name != "":
            self.db.execute("SELECT NAME, DESCRIPTION, EMAIL, USERNAME, PASSWORD, ACCESS_CODE, WEBSITE, "
                            "ADDRESS, PHONE_NUMBER, MISCELLANEOUS_INFO, PENDING_TASKS, DATE_MODIFIED "
                            "FROM accounts WHERE NAME = ?;", (name,))
            accountInfo = self.db.fetchone()

        # GET THE CATEGORIES TO DISPLAY
        displayCategories = ["NAME", "DESCRIPTION", "EMAIL", "USERNAME", "PASSWORD", "CODE", "WEBSITE",
                             "ADDRESS", "PHONE NUMBER", "MISC INFO", "PENDING TASKS", "DATE MODIFIED"]

        count = 0
        for info in accountInfo:
            if info != "" and count == 0 or count == 2 or count == 5:
                print("%s:\t\t%s" % (displayCategories[count], self.decode(info)))
            elif info != "":
                print("%s:\t%s" % (displayCategories[count], self.decode(info)))
            count += 1
