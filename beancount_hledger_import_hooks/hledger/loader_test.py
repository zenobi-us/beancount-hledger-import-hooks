from pathlib import Path

from beancount_hledger_import_hooks.hledger.loader import hledgerblocks
from beancount_hledger_import_hooks.mappers import (
    TransactionRuleMapper,
    TransformMapper,
)

here = Path(__file__).parent


def test_hledgerblocks():
    rules_path = here / "fixtures/all.rules"
    assert rules_path.exists()

    blocks = hledgerblocks(rules_path)

    assert blocks
    assert len(blocks.rules) == 22
    for rule in blocks.rules:
        assert isinstance(rule, TransactionRuleMapper)
        assert rule.matchers
        assert rule.transforms


def test_hledgerblocks_taxrules():
    rules_path = here / "fixtures/finance.tax.rules"
    assert rules_path.exists()

    blocks = hledgerblocks(rules_path)

    assert blocks
    assert len(blocks.rules) == 3

    assert isinstance(blocks.rules[0], TransactionRuleMapper)
    assert len(blocks.rules[0].matchers) == 1
    assert len(blocks.rules[0].transforms) == 2

    assert isinstance(blocks.rules[0].transforms[0], TransformMapper)
    assert blocks.rules[0].transforms[0].key == "account2"
    assert blocks.rules[0].transforms[0].value == "expenses:self:tax:accountant"

    assert isinstance(blocks.rules[0].transforms[1], TransformMapper)
    assert blocks.rules[0].transforms[1].key == "comment"
    assert blocks.rules[0].transforms[1].value == "icon:🧑‍💼"
