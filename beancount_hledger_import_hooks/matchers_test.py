from beancount_hledger_import_hooks.interrogator import JinjaInterrogator
from beancount_hledger_import_hooks.matchers import (
    AndMatcher,
    Matcher,
    OrMatcher,
    ResolveQuery,
)


def test_logicgate_and():
    interrogator = JinjaInterrogator()
    query = Matcher(
        "'Debit' in Transaction.Description",
        "'Wholefoods' in Transaction.Description",
        kind="And",
    )

    assert ResolveQuery({"Description": "Debit Wholefoods"}, interrogator, query)
    assert not ResolveQuery({"Description": "Debit"}, interrogator, query)
    assert not ResolveQuery({"Description": "Wholefoods"}, interrogator, query)
    assert not ResolveQuery({"Description": "Credit"}, interrogator, query)


def test_logicgate_or():
    interrogator = JinjaInterrogator()
    query = Matcher(
        "'Debit' in Transaction.Description",
        "'Wholefoods' in Transaction.Description",
        kind="Or",
    )

    assert ResolveQuery({"Description": "Debit"}, interrogator, query)
    assert ResolveQuery({"Description": "Wholefoods"}, interrogator, query)
    assert ResolveQuery({"Description": "Debit Wholefoods"}, interrogator, query)
    assert not ResolveQuery({"Description": "Credit"}, interrogator, query)
    assert ResolveQuery({"Description": "Credit Debit"}, interrogator, query)


def test_logicgate_not():
    interrogator = JinjaInterrogator()
    query = Matcher(
        "'Debit' in Transaction.Description",
        kind="Not",
    )

    assert not ResolveQuery({"Description": "Debit"}, interrogator, query)
    assert ResolveQuery({"Description": "Credit"}, interrogator, query)
    assert not ResolveQuery({"Description": "Credit Debit"}, interrogator, query)


def test_nested_logic():
    interrogator = JinjaInterrogator()

    query = OrMatcher(
        AndMatcher(
            "'Debit' in Transaction.Description",
            "'Wholefoods' in Transaction.Description",
        ),
        "'Groceries' in Transaction.Description",
    )

    assert ResolveQuery({"Description": "Debit Wholefoods"}, interrogator, query)
    assert ResolveQuery({"Description": "Groceries"}, interrogator, query)
    assert not ResolveQuery({"Description": "Debit"}, interrogator, query)
    assert not ResolveQuery({"Description": "Wholefoods"}, interrogator, query)
    assert not ResolveQuery({"Description": "Credit"}, interrogator, query)
    assert not ResolveQuery({"Description": "Credit Debit"}, interrogator, query)
    assert ResolveQuery({"Description": "Groceries Debit"}, interrogator, query)
    assert ResolveQuery({"Description": "Groceries Wholefoods"}, interrogator, query)
