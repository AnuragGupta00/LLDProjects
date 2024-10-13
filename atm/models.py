from abc import abstractmethod
from abc import ABC
from enum import Enum


class BankAccount:
    def __init__(self, holder_name, account_number, initial_balance):
        self.holder_name = holder_name
        self.account_number = account_number
        self.balance = initial_balance

    def get_balance(self):
        return self.balance

    def set_balance(self, new_balance):
        self.balance = new_balance
        return f"Balance updated to {self.balance}"

class TransactionType(Enum):
    CREDIT = "0"
    DEBIT = "1"
    BALANCE_CHECK = "2"



class Card:
    def __init__(self, card_number: str, bankAccount: BankAccount, pin: str):
        self.card_number: str = card_number
        self.account: BankAccount = bankAccount
        self.pin = pin

    def check_pin(self, user_supplied_pin: str):
        return self.pin == user_supplied_pin

    def withdraw_balance(self, amount: int):
        if self.account.get_balance() >= amount:

        print(f"Withdrawing {amount} Balance")

class WithdrawProcessor:
    def __init__(self, denomination, total_units, next_handler):
        self.next_handler = next_handler
        self.denomination = denomination
        self.total_units = total_units

    def handle_withdraw(self, atm, amount: float):
        if self.denomination * self.total_units >= amount:
            return f"Handled"
        else:
            self.next_handler.handle_withdraw(amount)


class HundredRupeesWithdrawProcessor(WithdrawProcessor):
    def __init__(self, next_handler = None, total_notes = 10):
        super().__init__(next_handler)


class ATM:
    def __init__(self):
        self.current_state = None


    def get_current_state(self):
        return self.current_state

    def set_current_state(self, state):
        self.current_state = state


class AbstractATMState(ABC):
    def __init__(self):
        pass


    def insert_card(self, atm: ATM ,card: Card):
        print(f"Not supported")
        return

    def authenticate_pin(self, atm: ATM, card: Card, pin: str):
        print(f"Not supported")
        return

    def select_operation(self, atm: ATM, card: Card):
        print(f"Not supported")
        return

    def check_balance(self, atm: ATM, card: Card):
        print(f"Not supported")
        return

    def withdraw_money(self, atm: ATM, card: Card, amount: int):
        print(f"Not supported")
        return

    def return_card(self, atm: ATM, card: Card):
        print(f"Not supported")
        return


class IdleState(AbstractATMState):
    def __init__(self):
        super().__init__()

    def insert_card(self, atm: ATM ,card: Card):
        print(f"Card is inserted")
        atm.set_current_state(HasCardState())


class HasCardState(AbstractATMState):
    def __init__(self):
        super().__init__()

    def authenticate_pin(self, atm: ATM, card: Card, pin: str):
        print(f"Checking card pin")
        if card.check_pin(pin):
            print(f"Card pin is valid")
            atm.set_current_state(AccountViewState())
        else:
            print(f"Card pin is invalid")
            print("Renter pin")

class AccountViewState(AbstractATMState):
    def __init__(self):
        super().__init__()
        self.withdraw_processor = None

    def select_operation(self, atm: ATM, operation_type: TransactionType):
        if operation_type == TransactionType.CREDIT:
            print(f"Not supported yet.")
        elif operation_type == TransactionType.DEBIT:
            print(f"Processing Withdrawal Request")
        elif operation_type == TransactionType.BALANCE_CHECK:
            print("Checking Balance")



    def check_balance(self, atm: ATM, card: Card):
        print(f"Balance is: {card.account.get_balance()}")
        return card.account.get_balance()


    def withdraw_money(self, atm: ATM, card: Card, amount: int):
        if self.check_balance(atm, card) < amount:
            print(f"Not possible to withdraw money")
        card.withdraw_balance(amount)
        self.withdraw_processor.withdraw(atm, amount)


