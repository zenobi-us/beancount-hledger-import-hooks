from decimal import Decimal

from beancount import loader

from beancount_hledger_import_hooks.interrogator import JinjaInterrogator
from beancount_hledger_import_hooks.transform import Transform, pasrse_posting

interrogator = JinjaInterrogator()
transactions, _, __ = loader.load_string("""
    2016-01-06 * "Debit Wholefoods"
        Assets:Bank:Account    1.06 USD

    2016-01-07 * "Debit"
        Assets:Bank:Account    1.06 USD

    2016-01-08 * "Wholefoods"
        Assets:Bank:Account    1.06 USD

    2016-01-09 * "Credit"
        Assets:Bank:Account    1.06 USD

    2016-01-10 * "Groceries"
        Assets:Bank:Account    1.06 USD

    2016-01-11 * "Groceries Wholefoods"
        Assets:Bank:Account    1.06 USD

    2016-01-12 * "Groceries Debit"
        Assets:Bank:Account    1.06 USD
""")


def test_pasrse_posting():
    """
    Test the pasrse_posting function.
    """

    result = pasrse_posting("Assets:Bank:Account 1.06 USD")

    assert result.account == "Assets:Bank:Account"
    assert result.units.number == Decimal("1.06")
    assert result.units.currency == "USD"


def test_transform_add_expense_account():
    """
    Test a transform that does nothing.
    """
    transformer = Transform(field="account2", template="Expenses:Food:Groceries")
    result = transformer.transform(transaction=transactions[0])

    assert result.postings[0].account == "Assets:Bank:Account"
    assert result.postings[1].account == "Expenses:Food:Groceries"


def test_transform_account_modify_account1():
    """
    Test a transform that does nothing.
    """
    transformer = Transform(
        field="account",
        template="Assets:Bank:FoodAccount    {{ Transaction.postings.0.units.number }} {{ Transaction.postings.0.units.currency }}",
    )
    result = transformer.transform(transaction=transactions[0])

    assert result.postings[0].account == "Assets:Bank:FoodAccount"
    assert result.postings[0].units.number == Decimal("1.06")
    assert result.postings[0].units.currency == "USD"
