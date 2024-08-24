from beancount import loader

from beancount_hledger_import_hooks.interrogator import JinjaInterrogator
from beancount_hledger_import_hooks.matchers import (
    AndMatcher,
    Matcher,
    OrMatcher,
    ResolveQuery,
)

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


def test_logicgate_and():
    query = Matcher(
        "'Debit' in Transaction.narration",
        "'Wholefoods' in Transaction.narration",
        kind="And",
    )

    assert ResolveQuery(transactions[0], interrogator, query)
    assert not ResolveQuery(transactions[1], interrogator, query)
    assert not ResolveQuery(transactions[2], interrogator, query)
    assert not ResolveQuery(transactions[3], interrogator, query)


def test_logicgate_or():
    query = Matcher(
        "'Debit' in Transaction.narration",
        "'Wholefoods' in Transaction.narration",
        kind="Or",
    )

    assert ResolveQuery(transactions[0], interrogator, query)
    assert ResolveQuery(transactions[1], interrogator, query)
    assert ResolveQuery(transactions[2], interrogator, query)
    assert not ResolveQuery(transactions[3], interrogator, query)


def test_logicgate_not():
    query = Matcher(
        "'Debit' in Transaction.narration",
        kind="Not",
    )

    assert not ResolveQuery(transactions[0], interrogator, query)
    assert not ResolveQuery(transactions[1], interrogator, query)
    assert ResolveQuery(transactions[2], interrogator, query)
    assert ResolveQuery(transactions[3], interrogator, query)


def test_nested_logic():
    query = OrMatcher(
        AndMatcher(
            "'Debit' in Transaction.narration",
            "'Wholefoods' in Transaction.narration",
        ),
        "'Groceries' in Transaction.narration",
    )

    assert ResolveQuery(transactions[0], interrogator, query)
    assert not ResolveQuery(transactions[1], interrogator, query)
    assert not ResolveQuery(transactions[2], interrogator, query)
    assert not ResolveQuery(transactions[3], interrogator, query)
    assert ResolveQuery(transactions[4], interrogator, query)
    assert ResolveQuery(transactions[5], interrogator, query)
    assert ResolveQuery(transactions[6], interrogator, query)
