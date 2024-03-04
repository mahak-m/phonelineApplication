"""
CSC148, Winter 2024
Assignment 1

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2022 Bogdan Simion, Diane Horton, Jacqueline Smith
"""
import datetime
from math import ceil
from typing import Optional
from bill import Bill
from call import Call

# Constants for the month-to-month contract monthly fee and term deposit
MTM_MONTHLY_FEE = 50.00
TERM_MONTHLY_FEE = 20.00
TERM_DEPOSIT = 300.00

# Constants for the included minutes and SMSs in the term contracts (per month)
TERM_MINS = 100

# Cost per minute and per SMS in the month-to-month contract
MTM_MINS_COST = 0.05

# Cost per minute and per SMS in the term contract
TERM_MINS_COST = 0.1

# Cost per minute and per SMS in the prepaid contract
PREPAID_MINS_COST = 0.025


class Contract:
    """ A contract for a phone line

    This class is not to be changed or instantiated. It is an Abstract Class.

    === Public Attributes ===
    start:
         starting date for the contract
    bill:
         bill for this contract for the last month of call records loaded from
         the input dataset
    """
    start: datetime.date
    bill: Optional[Bill]

    def __init__(self, start: datetime.date) -> None:
        """ Create a new Contract with the <start> date, starts as inactive
        """
        self.start = start
        self.bill = None

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ A new month has begun corresponding to <month> and <year>.
        This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.

        DO NOT CHANGE THIS METHOD
        """
        raise NotImplementedError

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        self.bill.add_billed_minutes(ceil(call.duration / 60.0))

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        self.start = None
        return self.bill.get_cost()


class TermContract(Contract):
    """
    A contract in which the customer must pay according
    to a fixed term, with a specified start and end date.

    === Public Attributes ===
    start:
         This is the starting date for the contract
    end:
        This is the date at which the contract ends.
    bill:
        This is the bill for this contract for the last month of call
         records loaded from the input dataset.
    current:
        This is the current date, updated every time months advance.
    """
    start: datetime.date
    current: datetime.date
    bill: Optional[Bill]
    end: datetime.date

    def __init__(self, start: datetime.date, end: datetime.date) -> None:
        """ Create a new TermContract with the <start> date, starts as inactive.
        """
        Contract.__init__(self, start)
        self.bill = None
        self.current = start
        self.end = end

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """
        This method overrides the method in the superclass because
        it is an abstract (uninitiated) method.

        Advance to a new month in the term contract (either an already
        existing contract or the first month of the contract). Store the
        <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.
        """
        # store the bill argument
        self.bill = bill
        # set rates using pre-defined constant
        self.bill.set_rates('TERM', TERM_MINS_COST)

        first_month = self.start.month
        first_year = self.start.year

        if first_month == month and first_year == year:
            self.bill.add_fixed_cost(TERM_DEPOSIT)

        # add fixed cost
        self.bill.add_fixed_cost(TERM_MONTHLY_FEE)

        # add free minimum
        # self.bill.free_min = 0

        # update current date
        self.current = datetime.date(year, month, 1)

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        if self.bill.free_min >= TERM_MINS:
            self.bill.add_billed_minutes(ceil(call.duration / 60.0))
        else:
            self.bill.add_free_minutes(ceil(call.duration / 60.0))

    def cancel_contract(self) -> float:
        """
        This method overrides the <cancel_contract> method from the
        Contract class. This is done to add certain specifications
        that account for differences in the term-to-term contract.
        """
        # set self.start to None
        self.start = None

        # CASE ONE -> this indicates that it is forfeited
        # (so the customer must pay everything)
        if self.current <= self.end:
            return self.bill.get_cost()

        else:  # customer gets deposit - months cost back
            # self.bill.add_fixed_cost((-1) * TERM_DEPOSIT)
            # return (- 1 * TERM_DEPOSIT) + self.bill.get_cost()
            return_v = (- 1 * TERM_DEPOSIT) + self.bill.get_cost()
            return return_v


class MTMContract(Contract):
    """
    A contract in which the phone line's billing is done on a
    month-to-month basis.

    === Public Attributes ===
    start:
         This is the starting date for the contract
    bill:
        This is the bill for this contract for the last month of call
         records loaded from the input dataset.

    === Preconditions ===
    Assume that the customer pays the bill on time each month.
    """
    start: datetime.date
    bill: Optional[Bill]

    def __init__(self, start: datetime.date) -> None:
        """ Create a new TermContract with the <start> date, starts as inactive.
        """
        Contract.__init__(self, start)
        self.bill = None

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """
        This method overrides the method in the superclass because
        it is an abstract (uninitiated) method.

        Advance to a new month in the term contract (either an already
        existing contract or the first month of the contract). Store the
        <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.
        """
        self.bill = bill
        # set the rates according to the provided constant
        self.bill.set_rates('MTM', MTM_MINS_COST)
        # no initial deposit so just add monthly fee
        self.bill.add_fixed_cost(MTM_MONTHLY_FEE)


class PrepaidContract(Contract):
    """ A contract in which there is a start date but not an end date, no
    included minutes and an associated balance.

    === Public Attributes ===
    bill:
         This is the bill for this contract for the last month of call
         records loaded from the input dataset.
    balance:
        the balance, where a negative value indicates credit

    === Preconditions ===
    Once again, assume that the customer pays the bill on time each month.
    """
    start: datetime.date
    bill: Optional[Bill]
    balance: float

    def __init__(self, start: datetime.date, balance: float) -> None:
        Contract.__init__(self, start)
        self.balance = - balance
        self.bill = None

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """
        Advance to a new month, corresponding to <month> and <year>.
        Then, store the <bill> argument in this argument. If the balance
        is less than $10, top up the balance with $25.
        """
        # store the <bill> argument
        self.bill = bill

        self.bill.add_fixed_cost(self.balance)
        self.bill.set_rates('PREPAID', PREPAID_MINS_COST)

        # later months: only method of payment/cycle = $25 top-up

        # now we have to consider the $25 top up
        if self.balance > -10:
            # self.balance -= -25
            self.bill.add_fixed_cost(-25)

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        self.bill.add_billed_minutes(ceil(call.duration / 60.0))

        # take away amount
        self.balance = self.balance + (
            ceil(call.duration / 60.0) * PREPAID_MINS_COST)

    def cancel_contract(self) -> float:
        """
        Return the amount owed. If the balance is negative, forfeit the
        balance. Otherwise, if it is positive, it is returned

        Precondition:
        Assume self.bill exists for the right month+year when the
        cancellation is requested
        """
        self.start = None

        if self.balance > 0:
            # return self.balance  # return cost
            return self.bill.get_cost()
        else:
            return 0  # amount forfeited


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'datetime', 'bill', 'call', 'math'
        ],
        'disable': ['R0902', 'R0913'],
        'generated-members': 'pygame.*'
    })
