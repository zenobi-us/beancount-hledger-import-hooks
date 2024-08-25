from decimal import Decimal

from beancount import loader

from beancount_hledger_import_hooks.interrogator import JinjaInterrogator
from beancount_hledger_import_hooks.mappers import (
    MatcherAndMapper,
    RuleSetMapper,
    TransactionRuleMapper,
    TransformMapper,
)
from beancount_hledger_import_hooks.rules import RuleSet


def test_ruleset_minimum_args():
    mapper = RuleSetMapper(rules=[])
    interrogator = JinjaInterrogator()
    ruleset = RuleSet.from_mapper(mapper=mapper, interrogator=interrogator)
    assert ruleset  # it exists
    assert ruleset.rules == []  # it has no rules
    assert (
        ruleset.run([]) == []
    )  # it returns an empty list (interrogator didn't explode)


def test_ruleset_satisfies():
    rule = TransactionRuleMapper(
        matchers=list(
            [
                MatcherAndMapper(and_is="'Debit' in Transaction.narration"),
                MatcherAndMapper(and_is="'Wholefoods' in Transaction.narration"),
            ]
        ),
        transforms=[
            TransformMapper(
                key="Account2", value="Expenses:Food:Groceries {{ Transaction.Amount }}"
            )
        ],
    )
    mapper = RuleSetMapper(rules=[rule])

    interrogator = JinjaInterrogator()

    transactions, _, __ = loader.load_string("""
        2016-01-06 * "Debit Wholefoods"
          Assets:Cash    1.06 USD
    """)

    ruleset = RuleSet.from_mapper(mapper=mapper, interrogator=interrogator)
    result = ruleset.run(transactions)

    assert len(result) == 1
    assert result[0].postings[0].account == "Assets:Cash"
    assert result[0].postings[0].units.number == Decimal("1.06")
    assert result[0].postings[1].account == "Expenses:Food:Groceries"
