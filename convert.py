import csv
from decimal import Decimal
import fnmatch
import os
import sys

input_file_name_pattern = 'Monefy.Data.*.csv'
input_file_name = 'input.csv'
output_accounts_file_name = '01_accounts.csv'
output_transfers_file_name = '02_transfers.csv'
output_transactions_file_name = '03_transactions.csv'

def findFile(pattern, path):
    result = []

    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))

    return result

def formatDate(date):
    return date.replace('/', '.')

def stripNbsp(str):
    return str.replace(u"\u00A0", '')

def formatAmount(amount):
    return '{0:.2f}'.format(Decimal(stripNbsp(amount)))

try:
    input_file_name = sys.argv[1]
    print('Using specified file name argument "{}"'.format(input_file_name))
except IndexError:
    print('Looking for a file name matching "{}" pattern in the directory'.format(input_file_name_pattern))
    files = findFile(input_file_name_pattern, '.')
    if len(files):
        input_file_name = files[0]
        print('Found "{}" file name'.format(input_file_name))
    else:
        print('Trying default "{}" file name'.format(input_file_name))

if not os.path.exists(input_file_name):
    sys.exit('File "{}" not found'.format(input_file_name))

with open(input_file_name, 'rt', encoding='utf-8', newline='') as file:
    reader = csv.reader(file, delimiter=';')
    header = next(reader)
    accounts = {}
    transactions = []
    transfersQ = []
    transfers = []

    for row in reader:
        date = row[0]
        account = row[1]
        category = row[2]
        amount = row[3]
        currency = row[4]
        description = row[7]

        # collect new Account
        if not account in accounts:
            accounts[account] = [account, currency, 0]
        # update Account with initial balance if any
        if category == "Initial balance '{}'".format(account):
            accounts[account] = [account, currency, stripNbsp(amount)]
            continue

        # store Transfer FROM
        if category.startswith("To '"):
            accountFrom = account
            accountTo = category[4:-1]
            transfersQ.append([date, accountFrom, accountTo, amount])
            continue

        # match with Transfer TO
        if category.startswith("From '"):
            accountTo = account
            accountFrom = category[6:-1]
            transferFrom = transfersQ.pop(0)

            if (transferFrom[0] != date or transferFrom[1] != accountFrom or transferFrom[2] != accountTo):
                sys.exit('Incorrect transfer order at line "{}"'.format(row))

            transfers.append([formatDate(date), accountFrom, stripNbsp(transferFrom[3]), accountTo, stripNbsp(amount), formatAmount(amount)])
            continue

        # general Transaction
        transactions.append([formatDate(date), account, category, stripNbsp(amount), description])

with open(output_accounts_file_name, 'wt', encoding='utf-8', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(['Счет', 'Валюта', 'Начальный остаток'])
    for accountName, accountData in dict(sorted(accounts.items())).items():
        writer.writerow(accountData)

with open(output_transfers_file_name, 'wt', encoding='utf-8', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(['Дата', 'Счет', 'Сумма (расход)', 'Счёт-получатель перевода', 'Сумма (доход)', 'Сумма (доход) округленная'])
    for transfer in transfers:
        writer.writerow(transfer)

with open(output_transactions_file_name, 'wt', encoding='utf-8', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(['Дата', 'Счет', 'Категория', 'Сумма со сзнаком', 'Комментарий'])
    for transaction in transactions:
        writer.writerow(transaction)

