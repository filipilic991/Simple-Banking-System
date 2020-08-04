#STEP 4 START
import random
import sqlite3


def check_luhn_algo(checkme):
    converting_to_int_list = []
    for item in list(checkme):
        converting_to_int_list.append(int(item))
    luhn_card_no = converting_to_int_list[:-1]
    tmp_list = luhn_card_no.copy()
    for i in range(0, len(tmp_list), 2):
        tmp_list[i] *= 2
        if tmp_list[i] > 9:
            tmp_list[i] -= 9
    checksum = list(str(10 - sum(tmp_list) % 10))
    if len(checksum) != 1:
        #print("CORRECTED !!!!")
        checksum = [0]
    #print("BEFORE CHECKSUM TEMP NO: {}, BEFORE CHECKSUM TEMP LENGTH: {}, TEMP SUM: {}".format(tmp_list, len(tmp_list), sum(tmp_list)))
    #print("CHECKSUM: {}, CHECKSUM LENGTH: {}".format(checksum, len(checksum)))
    luhn_card_no.extend(checksum)
    del tmp_list
    card_no_for_db = ''.join(map(str, luhn_card_no))
    if card_no_for_db == checkme:
        return True
    else:
        return False


def create_card():
    def get_pin():
        pin = ""
        for each in random.sample(range(9), k=4):
            pin += str(each)
        return pin

    conn = sqlite3.connect("card.s3db")
    curr = conn.cursor()
    iin = [4, 0, 0, 0, 0, 0]
    random_acc_no = random.sample(range(9), 9)
    luhn_card_no = []
    luhn_card_no.extend(iin)
    luhn_card_no.extend(random_acc_no)
    tmp_list = luhn_card_no.copy()
    for i in range(0, len(tmp_list), 2):
        tmp_list[i] *= 2
        if tmp_list[i] > 9:
            tmp_list[i] -= 9
    checksum = list(str(10 - sum(tmp_list) % 10))
    if len(checksum) != 1:
        #print("CORRECTED !!!!")
        checksum = [0]
    #print("BEFORE CHECKSUM TEMP NO: {}, BEFORE CHECKSUM TEMP LENGTH: {}, TEMP SUM: {}".format(tmp_list, len(tmp_list), sum(tmp_list)))
    #print("CHECKSUM: {}, CHECKSUM LENGTH: {}".format(checksum, len(checksum)))
    luhn_card_no.extend(checksum)
    del tmp_list
    card_no_for_db = ''.join(map(str, luhn_card_no))
    card_pin_for_db = get_pin()
    print("\nYour card has been created")
    print("Your card number:\n{}\nYour card PIN:\n{}\n".format(card_no_for_db, card_pin_for_db))
    curr.execute('SELECT id from card;')
    db_return = curr.fetchall()
    #flatten = lambda l: [item for sublist in l for item in sublist]
    try:
        listofrows = (lambda l: [item for sublist in l for item in sublist])(db_return)
        myid = max(listofrows)
    except ValueError:
        myid = 0
    dontsqlinjectme = (myid, card_no_for_db, card_pin_for_db)
    curr.execute('INSERT INTO card (id, number, pin) VALUES (?, ?, ?);', dontsqlinjectme)
    conn.commit()


def retrieve_from_db(user_enters_card_no, user_enters_pin):
    conn = sqlite3.connect("card.s3db")
    curr = conn.cursor()
    card_number = user_enters_card_no
    pin = user_enters_pin
    dontsqlinjectme = (card_number, pin)
    curr.execute('SELECT number, pin FROM card WHERE number = ? and pin = ?;', dontsqlinjectme)
    db_return = curr.fetchone()
    match = False
    try:
        if card_number in db_return and pin in db_return:
            match = True
            print("You have successfully logged in!")
    except sqlite3.OperationalError:
        print("\nWrong card number or PIN!\n")
    except TypeError:
        print("\nWrong card number or PIN!\n")
    while match:
        print("1. Balance\n2. Add income\n3. Transfer money\n4. Close account\n5.Log out\n0.Exit")
        second_menu_choice = int(input())
        if second_menu_choice == 1:
            curr.execute('SELECT balance FROM card WHERE number = ? and pin = ?;', (card_number, pin))
            db_return = curr.fetchone()
            print("\nBalance: {}\n".format(db_return[0]))
            #test = ("card",)
            #curr.execute('PRAGMA table_info({});'.format("card"))
            #db_return = curr.fetchall()
            #print("Balance: {}".format(db_return))
        elif second_menu_choice == 2:
            print("\nEnter income:")
            dontsqlinjectme = (int(input()), card_number, pin)
            curr.execute('UPDATE card SET balance = balance + ? WHERE number = ? and pin = ?;', dontsqlinjectme)
            conn.commit()
            print("Income was added!")
        elif second_menu_choice == 3:
            global transfer_destination
            transfer_destination = []
            print("Enter card number:")
            user_enters_transferdest = input()
            if len(user_enters_transferdest) != 16:
                print("\nProbably you made a mistake in the card number.\nPlease try again!\n")
                continue
            elif len(user_enters_transferdest) == 16:
                if user_enters_transferdest == card_number:
                    print("\nYou can't transfer money to the same account!\n")
                    continue
                elif not check_luhn_algo(user_enters_transferdest):
                    '# IF CHECK LUHN ALGO RETURNS FALSE. NOT FALSE = TRUE AND THEN WE CONTINUE'
                    print("\nLUHN CHECK:Probably you made a mistake in the card number.\nPlease try again!\n")
                    continue
                else:
                    transfer_destination = (int(user_enters_transferdest),)
            curr.execute('SELECT number FROM card WHERE number = ?;', transfer_destination)
            db_return = curr.fetchone()
            try:
                len(db_return)
                print("\nEnter how much money you want to transfer:\n")
                user_enters_transfermoney = int(input())
                curr.execute('SELECT balance FROM card WHERE number = ? and pin = ?', (card_number, pin))
                db_return = curr.fetchone()
                #print(db_return)
                #flattened_db_return = (lambda l: [item for sublist in l for item in sublist])(db_return)
                if user_enters_transfermoney > db_return[0]:
                    print("\nNot enough money!\n")
                    continue
                else:
                    curr.execute('UPDATE card SET balance = balance + ? WHERE number = ?;', (
                        user_enters_transfermoney, int(user_enters_transferdest)))
                    curr.execute('UPDATE card SET balance = balance - ? WHERE number = ?;', (
                        user_enters_transfermoney, card_number))
                    conn.commit()
                    print("\nSuccess!\n")
                    continue
            except TypeError:
                print("\nSuch a card does not exist.\n")
                continue

        elif second_menu_choice == 4:
            dontsqlinjectme = (card_number, pin)
            curr.execute('DELETE FROM card WHERE number = ? and pin = ?;', dontsqlinjectme)
            conn.commit()
            print("\nThe account has been closed!\n")
            break
        elif second_menu_choice == 5:
            print("You have successfully logged out!")
            match = False
        elif second_menu_choice == 0:
            print("Bye!")
            conn.close()
            exit()


def create_db():
    conn = sqlite3.connect("card.s3db")
    curr = conn.cursor()
    try:
        curr.execute('create table card (id INTEGER, number TEXT, pin TEXT, balance INTEGER default 0);')
    except sqlite3.OperationalError:
        curr.execute('DROP TABLE card;')
        curr.execute('create table card (id INTEGER, number TEXT, pin TEXT, balance INTEGER default 0);')
    finally:
        conn.commit()


program_is_running = True
create_db()
while program_is_running:
    print("1. Create an account\n2. Log into account\n0. Exit")
    first_menu_choice = int(input())
    if first_menu_choice == 1:
        create_card()
    elif first_menu_choice == 2:
        print("Enter your card number:")
        user_enters_card_no = input()
        print("Enter your PIN:")
        user_enters_pin = input()
        retrieve_from_db(user_enters_card_no, user_enters_pin)
    elif first_menu_choice == 0:
        print("Bye!")
        program_is_running = False
# STEP 4 END

'''#STEP 3 START
import random
import sqlite3


def create_card():
    def get_pin():
        pin = ""
        for each in random.sample(range(9), k=4):
            pin += str(each)
        return pin

    conn = sqlite3.connect("card.s3db")
    curr = conn.cursor()
    iin = [4, 0, 0, 0, 0, 0]
    random_acc_no = random.sample(range(9), 9)
    luhn_card_no = []
    luhn_card_no.extend(iin)
    luhn_card_no.extend(random_acc_no)
    tmp_list = luhn_card_no.copy()
    for i in range(0, len(tmp_list), 2):
        tmp_list[i] *= 2
        if tmp_list[i] > 9:
            tmp_list[i] -= 9
    checksum = list(str(10 - sum(tmp_list) % 10))
    if len(checksum) != 1:
        #print("CORRECTED !!!!")
        checksum = [0]
    #print("BEFORE CHECKSUM TEMP NO: {}, BEFORE CHECKSUM TEMP LENGTH: {}, TEMP SUM: {}".format(tmp_list, len(tmp_list), sum(tmp_list)))
    #print("CHECKSUM: {}, CHECKSUM LENGTH: {}".format(checksum, len(checksum)))
    luhn_card_no.extend(checksum)
    del tmp_list
    card_no_for_db = ''.join(map(str, luhn_card_no))
    card_pin_for_db = get_pin()
    print("\nYour card has been created")
    print("Your card number:\n{}\nYour card PIN:\n{}\n".format(card_no_for_db, card_pin_for_db))
    curr.execute('SELECT id from card;')
    db_return = curr.fetchall()
    #flatten = lambda l: [item for sublist in l for item in sublist]
    try:
        listofrows = (lambda l: [item for sublist in l for item in sublist])(db_return)
        myid = max(listofrows)
    except ValueError:
        myid = 0
    dontsqlinjectme = (myid, card_no_for_db, card_pin_for_db)
    curr.execute('INSERT INTO card (id, number, pin) VALUES (?, ?, ?);', dontsqlinjectme)
    conn.commit()


def retrieve_from_db(user_enters_card_no, user_enters_pin):
    conn = sqlite3.connect("card.s3db")
    curr = conn.cursor()
    card_number = user_enters_card_no
    pin = user_enters_pin
    dontsqlinjectme = (card_number, pin)
    curr.execute('SELECT number, pin FROM card WHERE number = ? and pin = ?;', dontsqlinjectme)
    db_return = curr.fetchone()
    match = False
    try:
        if card_number in db_return and pin in db_return:
            match = True
            print("You have successfully logged in!")
    except sqlite3.OperationalError:
        print("\nWrong card number or PIN!\n")
    except TypeError:
        print("\nWrong card number or PIN!\n")
    while match:
        print("1. Balance\n2. Log out\n0. Exit")
        second_menu_choice = int(input())
        if second_menu_choice == 1:
            curr.execute('SELECT balance FROM card WHERE number = ? and pin = ?;', dontsqlinjectme)
            db_return = curr.fetchone()
            print("Balance: {}".format(db_return[0]))
            #test = ("card",)
            #curr.execute('PRAGMA table_info({});'.format("card"))
            #db_return = curr.fetchall()
            #print("Balance: {}".format(db_return))
        elif second_menu_choice == 2:
            print("You have successfully logged out!")
            match = False
        elif second_menu_choice == 0:
            print("Bye!")
            conn.close()
            exit()


def create_db():
    conn = sqlite3.connect("card.s3db")
    curr = conn.cursor()
    try:
        curr.execute('create table card (id INTEGER, number TEXT, pin TEXT, balance INTEGER default 0);')
    except sqlite3.OperationalError:
        curr.execute('DROP TABLE card;')
        curr.execute('create table card (id INTEGER, number TEXT, pin TEXT, balance INTEGER default 0);')
    finally:
        conn.commit()


program_is_running = True
create_db()
while program_is_running:
    print("1. Create an account\n2. Log into account\n0. Exit")
    first_menu_choice = int(input())
    if first_menu_choice == 1:
        create_card()
    elif first_menu_choice == 2:
        print("Enter your card number:")
        user_enters_card_no = input()
        print("Enter your PIN:")
        user_enters_pin = input()
        retrieve_from_db(user_enters_card_no, user_enters_pin)
    elif first_menu_choice == 0:
        print("Bye!")
        program_is_running = False
"""# STEP 3 END"""
'''
'''
# STEP 2 START (LUHN ALGORITHM)
import random


class Customer:
    user_accounts = []

    def __init__(self):
        def get_card_no():
            iin = [4, 0, 0, 0, 0, 0]
            random_acc_no = random.sample(range(9), 9)
            luhn_card_no = []
            luhn_card_no.extend(iin)
            luhn_card_no.extend(random_acc_no)
            tmp_list = luhn_card_no.copy()
            for i in range(0, len(tmp_list), 2):
                tmp_list[i] *= 2
                if tmp_list[i] > 9:
                    tmp_list[i] -= 9
            checksum = list(str(10 - sum(tmp_list) % 10))
            luhn_card_no.extend(checksum)
            del tmp_list
            return ''.join(map(str, luhn_card_no))

        def get_pin():
            pin = ""
            for each in random.sample(range(9), k=4):
                pin += str(each)
            #print("raw pin {} , pin len {}".format(pin, len(pin)))
            return pin

        self.card_number = get_card_no()
        self.pin = get_pin()
        self.balance = 0
        Customer.user_accounts.append(self)


program_is_running = True
while program_is_running:
    print("1. Create an account\n2. Log into account\n0. Exit")
    first_menu_choice = int(input())
    if first_menu_choice == 1:
        user = Customer()
        print("\nYour card has been created")
        print("Your card number:\n{}\nYour card PIN:\n{}\n".format(user.card_number, user.pin))
        #print(Customer.user_accounts)
    if first_menu_choice == 2:
        print("Enter your card number:")
        user_enters_card_no = input()
        print("Enter your PIN:")
        user_enters_pin = input()
        match = False
        account_index = ""
        for each in Customer.user_accounts:
            if user_enters_card_no == each.card_number and user_enters_pin == each.pin:
                match = True
                account_index = Customer.user_accounts.index(each)
                print("You have successfully logged in!")
                break
        else:
            print("\nWrong card number or PIN!\n")
        while match:
            print("1. Balance\n2. Log out\n0. Exit")
            second_menu_choice = int(input())
            if second_menu_choice == 1:
                print("Balance: {}".format(Customer.user_accounts[account_index].balance))
            if second_menu_choice == 2:
                print("You have successfully logged out!")
                match = False
            if second_menu_choice == 0:
                print("Bye!")
                exit()
    if first_menu_choice == 0:
        print("Bye!")
        program_is_running = False
# STEP 2 END (LUHN ALGORITHM)
'''
"""
# STEP 1 START
import random


class Customer:
    user_accounts = []

    def __init__(self):
        def get_card_no():
            iin = str(400000)
            acc_number = ""
            for each in random.sample(range(9), 9):
                acc_number += str(each)
            checksum = "5"
            return int(iin + acc_number + checksum)

        def get_pin():
            pin = ""
            for each in random.sample(range(9), k=4):
                pin += str(each)
            #print("raw pin {} , pin len {}".format(pin, len(pin)))
            return pin

        self.card_number = get_card_no()
        self.pin = get_pin()
        self.balance = 0
        Customer.user_accounts.append(self)


program_is_running = True
while program_is_running:
    print("1. Create an account\n2. Log into account\n0. Exit")
    first_menu_choice = int(input())
    if first_menu_choice == 1:
        user = Customer()
        print("\nYour card has been created")
        print("Your card number:\n{}\nYour card PIN:\n{}\n".format(user.card_number, user.pin))
        #print(Customer.user_accounts)
    if first_menu_choice == 2:
        print("Enter your card number:")
        user_enters_card_no = int(input())
        print("Enter your PIN:")
        user_enters_pin = input()
        match = False
        account_index = ""
        for each in Customer.user_accounts:
            if user_enters_card_no == each.card_number and user_enters_pin == each.pin:
                match = True
                account_index = Customer.user_accounts.index(each)
                print("You have successfully logged in!")
                break
        else:
            print("\nWrong card number or PIN!\n")
        while match:
            print("1. Balance\n2. Log out\n0. Exit")
            second_menu_choice = int(input())
            if second_menu_choice == 1:
                print("Balance: {}".format(Customer.user_accounts[account_index].balance))
            if second_menu_choice == 2:
                print("You have successfully logged out!")
                match = False
            if second_menu_choice == 0:
                print("Bye!")
                exit()
    if first_menu_choice == 0:
        print("Bye!")
        program_is_running = False
# STEP 1 END
"""