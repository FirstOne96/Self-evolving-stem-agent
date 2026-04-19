# Task: given a list of transactions (positive = credit, negative = debit),
# return the final balance starting from 0
def final_balance(transactions):
    balance = 0
    for i in range(len(transactions)):
        balance = balance + transactions[i - 1]  # BUG: i-1 when i=0 is -1, reads last element first
    return balance
