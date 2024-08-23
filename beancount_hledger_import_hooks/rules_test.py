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
                MatcherAndMapper(and_is="'Debit' in Transaction.Description"),
                MatcherAndMapper(and_is="'Wholefoods' in Transaction.Description"),
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

    ruleset = RuleSet.from_mapper(mapper=mapper, interrogator=interrogator)
    result = ruleset.run(transactions)

    assert len(result) == 1
    assert result[0]["Account2"] == "Expenses:Food:Groceries 100"
    # assert result[1]["Account2"] == "Expenses:Food:Groceries 100"
    # assert result[2]["Account2"] == "Expenses:Food:Groceries 100"
    # assert "Account2" not in result[3]
    # assert "Expenses:Food:Groceries" not in result[3]
