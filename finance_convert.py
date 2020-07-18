from os import listdir, path # List all files in directory and find file in path
from sys import argv # To get arguments that are passed to script

class FixDatabase:

    def write_to_file_with_quote_marks(self, line):
        ## This function adds quotation marks around every cell, appends new line character to the end of the line and writes that line to a file "_fixed"
        
        new_list = []
        
        for cell in line:
            
            new_list.append('"' + str(cell) + '"')
    
        joined_list_to_string = ";".join(new_list) #Seperates every list item by ; while joining it to string
        self.fixed_document.write(joined_list_to_string + "\n") # appends new line charakter to the string and writes it to the file.
    
    
    def fix_document(self):

        euro = "€"
    
        if len(argv) > 2:
            # If there are more than two variables passed to program it assumes that seconds variable is a file name that user wants to use as document with all accounts and third variable as file that user want to fix.
            account_file = argv[1]
            fix_file = argv[2]
        else:
            # Else user will have to choose files manually
            print("Choose a file that has all accounts that needs to be used:")
            account_file = choose_csv_file()
            print("Choose a file that has to be fixed:")
            fix_file = choose_csv_file() 
    
        # Opens all documents that will be used.
        account_document = open(account_file, mode="r", encoding="utf-8")
        account_document_lines = account_document.readlines()
    
        fix_document = open(fix_file, mode="r", encoding="utf-8") # Personal Finances pro document that will be fixed
        self.fixed_document = open(fix_file.rstrip(".csv") + "_fixed.csv", mode="w", encoding="utf-8") # Document that will be created will all the data inserted into it and ready to use.
    
        # Creating dictionaries that will be used to replace categories and insert bank accounts
        self.replace_accounts = self.create_dict_from_file("Account.ods")
        self.replace_categories = self.create_dict_from_file("Category.ods")


        for line in account_document_lines:
            ## Writes to _fixed.csv file all of the accounts that were exported from empty new database. 
            self.fixed_document.write(line)
        
        id_counter = len(account_document_lines) - 1 # Id counter do not have to match the line number or anything, but because it is new file and all transactions will be added later it will should be fine and deffinetly easier.
        id_group_counter = 0
    
        fix_document_lines = fix_document.readlines()

        for line in fix_document_lines[1:]:
            
            line = line.split(";")
    
            date = ""
            bank = ""
            account = ""
            number = ""
            mode = ""
            payee = ""
            comment = ""
            quantity = ""
            unit = ""
            amount = ""
            sign = ""
            category = ""
            status = ""
            tracker = ""
            bookmarked = ""
            id = ""
            idtransaction = ""
            idgroup = ""
            
            ## DATE ##
            date = line[2]
    
            ## NUMBER, MODE, PAYEE & TRACKER##
            # All these are not in use in my database. So i just leave them empty
            number = mode = payee = tracker = ""
            
            ## STATUSi & BOOKMARKED ##
            status = "Y"
            bookmarked = "N"
    
            ## COMMENT ##
            if line[1] != "" or line[0] != "":
                comment = self.join_comment_and_description(line[0], line[1])
            else:
                comment = ""
    
            ## CATEGORY ##
            category = self.replace_categories[line[4]][0]
            if len(line[4]) == 2:
                if comment == "":
                    comment += self.replace_categories[line[4][1]]
                else:
                    comment += ". " + self.replace_categories[line[4][1]]
    
            if path.exists("Comment_Category.ods"):
                # Checks if user created a "Comment_Category.ods" file
                comment_category_dict = self.create_dict_from_file("Comment_Category.ods") # Creates disctionary using file provided
                if comment in comment_category_dict:
                    # Checks if comment is in dictionary. Changes category and deletes old comment if true
                    category = comment_category_dict[comment][0]
                    comment = ""

            ## BANK, ACCOUNT, QUANTITY, UNIT, AMOUNT, SIGN, ID, IDTRANSACTION & IDGROUP##
            if line[9].find(":") == -1:
                ## This deals with line that has just one bank account involved
                bank = self.replace_accounts[line[9]][0] # Searches for a key in dictionary that was created from Accounts.ods. If user did everything fine it should work.
                account = self.replace_accounts[line[9]][1] # The same as bank
                quantity = line[18] # Simply gets from Personal Finances Pro database
                unit = self.replace_accounts[line[9]][2] # Same as bank and account.
                amount = str(round(float(line[18]) * float(self.replace_accounts[line[9]][3]),2)) # Calculates using values provided by user. Because of different ways Personal Finances Pro and Skrooge keeps records it is not possible to get an exact amount. 
                if line[18][0] == "-": # Depending on first symbol of "quantity" asigns value to "sign"
                    sign = "-"
                else:
                    sign = "+"
                id_counter += 1 # Adds +1 to id count
                id = idtransaction = id_counter # Asigns values to id and idtransactions
                idgroup = 0 # asigns value to idgroup
    
                fixed_line = [date, bank, account, number, mode, payee, comment, quantity, unit, amount, sign, category, status, tracker, bookmarked, id, idtransaction, idgroup]
                #print(fixed_line)
                ## Writing file to database ##
                self.write_to_file_with_quote_marks(fixed_line)
                
    
            else:
                # Adapts Personal Finances Pro transfers for Skrooge
                # First transfer
    
                # Only one idgroup per transfer
                id_group_counter += 1
                idgroup = id_group_counter
                #
                id_counter += 1 # Adds +1 to id count
                id = idtransaction = id_counter # Asigns values to id and idtransactions
    
                bank1 = self.replace_accounts[line[9].split(":")[0]][0]
                bank2 = self.replace_accounts[line[9].split(":")[1]][0]
                account1 = self.replace_accounts[line[9].split(":")[0]][1]
                account2 = self.replace_accounts[line[9].split(":")[1]][1]
                unit1 = self.replace_accounts[line[9].split(":")[0]][2]
                unit2 = self.replace_accounts[line[9].split(":")[1]][2]
                sign1 = "-"
                sign2 = "+"
                quantity1 = sign1 + line[12]
                 
                if unit1 == unit2:
                    # Both currencies are the same
                    if unit1 == euro:
                        # Both currencies are euros
                        # Simple, all values are the same. Just values in first line has "-" sign if fron of it.
                        amount1 = quantity1
                        quantity2 = amount2 = line[12]
                    else:
                        # Both are not euros
                        # Had to convert both "amount" values to euros because skrooge has this currency as default/base currency
                        amount1 = str(round(float(quantity1) * float(self.replace_accounts[line[9].split(":")[0]][3]),2))
                        quantity2 = line[13]
                        amount2 = str(round(float(quantity2) * float(self.replace_accounts[line[9].split(":")[1]][3]),2))
                else:
                    # Account currencies are different
                    if unit1 == euro:
                        # First account has euros
                        amount1  = quantity1
                        quantity2 = line[13] # Personal Finances Pro saved this value as a amount for account that was not in euros during transaction.
                        amount2 = line[12] # Because Personal Finances Pro saves transactions in accounts values amount for second transaction matches amount for first transaction as far sa skrooge is concerned
                    elif unit2 == euro:
                        # Second account has euros
                        amount1 = sign1 + line[13] # Personal Finances saved Euro amount in target amount cell for euro account so nothing has to be calculated.
                        amount2 = quantity2 = line[13]
                    else:
                        # None of the accounts are in euros
                        # All is the same as "both are in euros" few lines above.
                        amount1 = str(round(float(quantity1) * float(self.replace_accounts[line[9].split(":")[0]][3]),2))
                        quantity2 = line[13]
                        amount2 = str(round(float(quantity2) * float(self.replace_accounts[line[9].split(":")[1]][3]),2))

    
                fixed_line = [date, bank1, account1, number, mode, payee, comment, quantity1, unit1, amount1, sign1, category, status, tracker, bookmarked, id, idtransaction, idgroup]
                #print(fixed_line)
                self.write_to_file_with_quote_marks(fixed_line)
    
                # Second transfer
                id_counter += 1 # Adds +1 to id count
                id = idtransaction = id_counter # Asigns values to id and idtransactions
    
    
                fixed_line = [date, bank2, account2, number, mode, payee, comment, quantity2, unit2, amount2, sign2, category, status, tracker, bookmarked, id, idtransaction, idgroup]
                #print(fixed_line)
                self.write_to_file_with_quote_marks(fixed_line)
    
    
        # Closes all opened documents before exiting
        account_document.close() # Closes file
        fix_document.close()
        self.fixed_document.close()
    
    def create_dict_from_file(self, file):
        # Simply creates a dictionary from a provided file for simplier use.
        file = open(file, mode="r", encoding="utf-8")
        file_lines = file.readlines()
    
        dictionary = dict()
    
        for line in file_lines:
            line = line.split(";")
            dictionary[line[0]] = []
            for item in range(1, len(line)-1):
                dictionary[line[0]].append(line[item])
            if line[-1] != "\n":
                dictionary[line[0]].append(line[-1].rstrip("\n"))
    
        return dictionary
        
    
    def join_comment_and_description(self, description, comment):
        ## Depending on values passed from columns description and comment joinded sting is returned
        description = description.replace('"', '')
        comment = comment.replace('"', '')
    
        if comment == "":
        # Most likely case that comment is empty. At least in my DB
            return description
        elif description == "":
            return comment
        else:
            if description[-1:] == ".":
                return description.replace('"', '') + " " + comment.replace('"', '')
            else:
                return description.replace('"', '') + ". " + comment.replace('"', '')
    
    def get_all_categories(self):
        ## Collects all valies from chosen column
        ## Offers user to save that list to a file that saves everything in new line
    
        file_for_categories = self.choose_csv_file() # user chooses a file to get categories from
        file_to_read = open(file_for_categories, mode="r", encoding="utf-8") # Opens chosen file as read only
    
        lines = file_to_read.readlines() # Makes a file as a list
    
        uniq_categories = [] # List that will contain all unique entries
        
        print("Choose category: ")
    
        categories = lines[0].split(";") # Splits first line of the file that contains categories
        
        for cat in range(len(categories)):
            # Prints options that are available
            print(str(cat) + " " + categories[cat])
        
        user_input = input("Write a number: ") # Waits for user input
    
        for line in lines[1:]:
            # Iterates throught every line
            chosen_col = line.split(";")[int(user_input)] # selects chosen column of that line
            if chosen_col not in uniq_categories:
                # If that line is not in the uniq_categories list. Appends it to list
                uniq_categories.append(chosen_col)
        
        print("There are " + str(len(uniq_categories)) + " unique entries")
        print(uniq_categories)
    
        print()
        print("Do you want to write these to file '" + categories[int(user_input)] + ".ods'")
    
        file_to_read.close()
        
        write_to_file = input("y/N? ")
        if write_to_file == "y":
            self.print_to_file(categories[int(user_input)] + ".ods", uniq_categories)
    
    def print_to_file(self, filename, list):
        ## Writes passed list to a file. User has to give a filename too.
    
        file_to_write_in = open(filename, mode="w", encoding="utf-8")
    
        for word in list:
            file_to_write_in.write(word + '\n')
    
        file_to_write_in.close()
    
    def choose_csv_file(self):
        ## Prints all .csv files in the directory and return the one that user chooses
    
        files_to_offer = []
    
        for i in range(len(listdir())):
            # Iterates though listdir (files in directory)
            if listdir()[i][-4:] == ".csv":
                # If file ends with .csv adds to list
                files_to_offer.append(listdir()[i])
    
        for i in range(len(files_to_offer)):
            # prints all available files with option numbers.
            print(str(i) + " " + files_to_offer[i])
    
        return files_to_offer[int(input("Type a number: "))] # asigns chosen filename to a variable


class JoinDatabases:
    ### It's better to import all the transactions as one file, because Skrooge will overwrite some of them because ID, IDTRANSACTION & IDGROUP may be the same.


    def __init__(self):
        ## Initiating things I will need.
        print("Choose a base file you want to use (Fixed Personal Finances Pro database)")
        file1 = self.choose_csv_file()
        self.base = open(file1, mode="r", encoding="utf-8")
        self.base_lines = self.base.readlines()
        self.base.close() # Closing this file here because I need to open in for writing.
        self.base = open(file1, mode="a", encoding="utf-8")
        print("Choose a file you want to append (exported database from Skrooge")
        print("Make sure that there are no mismatching 'bank' and 'account' names")
        file2 = self.choose_csv_file()
        self.append = open(file2, mode="r", encoding="utf-8")
        self.append_lines = self.append.readlines()
        
        if not self.check_bank_accounts():
            print("Missing/missmaching account between files")
            print("Please fix it before continueing")
        else:
            self.join_accounts()

    def choose_csv_file(self):
        ## Prints all .csv files in the directory and return the one that user chooses
    
        files_to_offer = []
    
        for i in range(len(listdir())):
            # Iterates though listdir (files in directory)
            if listdir()[i][-4:] == ".csv":
                # If file ends with .csv adds to list
                files_to_offer.append(listdir()[i])
    
        for i in range(len(files_to_offer)):
            # prints all available files with option numbers.
            print(str(i) + " " + files_to_offer[i])
    
        return files_to_offer[int(input("Type a number: "))] # asigns chosen filename to a variable

    def check_bank_accounts(self):
        ## Created to list. One with bank accounts from Personal Finances Pro fixed database, another - from skrooge database.
        ## Compares and prints user a message if it wasn't available to find one of the accounts.
        ## Returns True or Fallse depending in that.
        
        base_list = []
        append_list = []

        breaker = 0

        for line in self.base_lines:
            line = line.split(";")
            if line[0] == "0000-00-00":
                base_list.append(line[2])

        for line in self.append_lines:
            line = line.split(";")
            if line[0] == "0000-00-00":
                append_list.append(line[2])
        
        for item in append_list:
            if item not in base_list:
                breaker += 1
                print("Could not find " + item + " account in skrooge database")

        if breaker > 0:
            return False
        else:
            return True

    def join_accounts(self):
        ## Joins both documents together

        ## Settings all needed variables ##        
        id = len(self.base_lines) - 1 # because id and idtransaction are allways the same there are no need to make both.
        
        two_count = 0 # Could think of a better way to increase idgroup count every other line

        for line in self.base_lines[::-1]:
            line = line.rstrip("\n").split(";")
            if line[17].strip('"') != '0':
                idgroup = int(line[17].strip('"')) + 1 # Removing quotes, adding one and to last idgroup number from Personal Finances Pro fixed database and setting it to new idgroup number tgat will be used fron now on
                break
        
        for line in self.append_lines[1:]:
            line = line.rstrip("\n").split(";")
            if line[0] != "0000-00-00":
                id += 1
                new_line = line[:-3]
                new_line.append(str(id))
                new_line.append(str(id))
                if line[17] != "0":
                    if two_count == 2:
                        idgroup += 1
                        two_count = 0
                    two_count += 1
                    new_line.append(str(idgroup))
                else:
                    new_line.append("0")
                #print(new_line)
                self.write_to_file_with_quote_marks(new_line)

        self.base.close()
        self.append.close()
                    
    def write_to_file_with_quote_marks(self, line):
        ## This function adds quotation marks around every cell, appends new line character to the end of the line and appends to Personal Finances Pro Fixed file. (User had to select it in the begining)
        
        new_list = []
        
        for cell in line:
            
            new_list.append('"' + str(cell) + '"')
    
        joined_list_to_string = ";".join(new_list) #Seperates every list item by ; while joining it to string
        self.base.write(joined_list_to_string + "\n") # appends new line charakter to the string and writes it to the file.

###
### This part starts the program by asking what user wants to do.
### Depending on the asnwer executes a function
###

fix_database= FixDatabase()

options = ["Get categories", "Fix a database", "Join Databases"]
print("What do you want to do?")

for item in range(len(options)):
    print(str(item) + ") " + options[item]) 

user_choice = input("Write an option number: ")

if user_choice == "0":
    fix_database.get_all_categories()
elif user_choice == "1":
    fix_database.fix_document()
elif user_choice == "2":
    join_databases = JoinDatabases()

