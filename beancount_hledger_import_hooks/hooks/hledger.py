import threading
from pathlib import Path
from typing import Callable

from beancount.core import data as beancount_datatypes
from smart_importer.hooks import ImporterHook

from beancount_hledger_import_hooks.hledger.loader import hledgerblocks
from beancount_hledger_import_hooks.interrogator import (
    InterrogatorBase,
    JinjaInterrogator,
)
from beancount_hledger_import_hooks.rules import RuleSet


class WithHledgerRules(ImporterHook):
    """A hook that applies a series of ledger rules to imported transactions."""

    interrogator: InterrogatorBase

    def __init__(self, rules_path: Path | None = None):
        self.rules_path = rules_path

        if self.rules_path is None:
            raise ValueError("rules_path is required")

        blocks = hledgerblocks(self.rules_path)
        self.rules = RuleSet.from_mapper(mapper=blocks)
        self.interrogator = JinjaInterrogator(
            date_format=self.rules.options.date_format
        )
        self.lock = threading.Lock()

    def __call__(
        self,
        importer: Callable,
        file: str,
        imported_entries: beancount_datatypes.Entries,
        existing_entries: beancount_datatypes.Entries,
    ):
        """Runs a series of ledger rules over imported transactions.

        Args:
            imported_entries: The list of imported entries.
            existing_entries: The list of existing entries

        Returns:
            A list of entries, modified by this hook.
        """
        self.account = importer.file_account(file)

        result = []

        with self.lock:
            result = self.rules.run(
                transactions=imported_entries, interrogator=self.interrogator
            )

        return result
