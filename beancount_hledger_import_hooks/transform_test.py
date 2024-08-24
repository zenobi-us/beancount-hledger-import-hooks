from beancount import loader

from beancount_hledger_import_hooks.interrogator import JinjaInterrogator
from beancount_hledger_import_hooks.transform import Transform

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


def test_transform_noop():
    """
    Test a transform that does nothing.
    """
    transform = Transform(field="account2", template="{{ Transaction.Account }}")
    assert (
        transform.transform(transactions[0]).postings[0].account
        == "Assets:Bank:Account"
    )
