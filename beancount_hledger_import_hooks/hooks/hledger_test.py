import unittest
from pathlib import Path

from beancount.ingest import regression_pytest
from beancount.ingest.importers import csv
from beancount.ingest.importers.csv import Col
from smart_importer.hooks import apply_hooks

from beancount_hledger_import_hooks.hooks.hledger import WithHledgerRules


class Importer(csv.Importer):
    """Conventional importer for Agrimaster CSV files"""

    def __init__(self, *, account, matchers=None):
        self.matchers = matchers or []
        super().__init__(
            {
                Col.ACCOUNT: 0,
                Col.DATE: 1,
                Col.NARRATION: 3,
                Col.AMOUNT_DEBIT: 4,
                Col.BALANCE: 5,
            },
            account,
            "AUD",
        )


here = Path(__file__).parent
root = here.parent
directory = here / "fixtures"

hledger_hook = WithHledgerRules(rules_path=root / "hledger" / "fixtures" / "all.rules")


importer = apply_hooks(
    Importer(
        account="Assets:Bank:Checking",
    ),
    [hledger_hook],
)


@regression_pytest.with_importer(importer)
@regression_pytest.with_testdir(directory)
class TestImporter(regression_pytest.ImporterTestBase):
    pass


if __name__ == "__main__":
    unittest.main()
