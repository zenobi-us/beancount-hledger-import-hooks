import threading
from typing import Callable

from beancount.core import data as beancount_datatypes
from smart_importer.hooks import ImporterHook

from beancount_hledger_import_hooks.interrogator import JinjaInterrogator
from beancount_hledger_import_hooks.rules import RuleSet
from beancount_hledger_import_hooks.yamlledger.loader import yamlblocks


class WithYamlRules(ImporterHook):
    def __init__(self, *args, **kwargs):
        self.rules_path = kwargs.get("rules_path", None)
        yamlruleset = yamlblocks(self.rules_path)
        interrogator = JinjaInterrogator()
        self.rules = RuleSet.from_mapper(mapper=yamlruleset, interrogator=interrogator)
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
        with self.lock:
            return self.rules.run(transactions=imported_entries)
