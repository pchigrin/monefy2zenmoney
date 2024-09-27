# monefy2zenmoney

Convert CSV data from Monefy to Zenmoney format

#### 1) In Monefy do export to CSV file (Settings -> Export to file)

#### 2) Put CSV file to the converter directory

#### 3) Run converter sript or executable

It will search for Monefy data file pattern "Monefy.Data.*.csv" and use first found

As alternative you can specify custom file name as a run parameter

#### As output you should have 3 files:
  - 01_accounts.csv - All accounts found with currency and initial balance
  - 02_transfers.csv - Transfers FROM - TO accounts
  - 03_transactions.csv - General transactions
