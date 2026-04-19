# A simple bank account. deposit and withdraw update the balance.
# is_overdrawn checks if balance is negative.
# The bug causes is_overdrawn to give wrong answers for near-zero balances.

class BankAccount:
    def __init__(self):
        self.balance = 0.0

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self, amount):
        self.balance -= amount

    def is_overdrawn(self):
        return self.balance < 0  # BUG: should use a small epsilon for float comparison
                                  # e.g. after deposit(0.1) three times and withdraw(0.3),
                                  # balance is -5.55e-17, not 0.0 — reports overdrawn incorrectly

    def get_balance(self):
        return round(self.balance, 10)
