# beancount-hledger-import-hooks

Your description

## Install

```sh
pip install beancount-hledger-import-hooks
```

or

```sh
poetry add beancount-hledger-import-hooks
```

## Usage

With `smart_importer` you can apply hooks to your importers.

````py
import sys
from os import path

from smart_importer import apply_hooks
from beancount_hledger_import_hooks.hooks import WithHledgerRules

from your_importers import a_kind_of_importer

importer_instance = a_kind_of_importer.Importer(
    account="Assets:YourBank:YourAccount",
    matchers=[
        ("filename", ".*0123456.*.csv"),
    ],
)

with_ledger_rules = WithHledgerRules(rules_path="hledger_rules/all.rules")

CONFIG = [
    apply_hooks(importer_instance, [with_ledger_rules]),
    apply_hooks(some_other_importer_instance, [with_ledger_rules]),
    apply_hooks(yet_more_importer, [with_ledger_rules]),
    apply_hooks(need_moar_impoter, [with_ledger_rules]),
]
````

or with vanilla beancount ingestor

```py
from beancount.core import data
from beancount.ingest import scripts_utils
from beancount.ingest import extract

from beancount_hledger_import_hooks.hooks import WithHledgerRules

from your_importers import a_kind_of_importer

importer_instance = a_kind_of_importer.Importer(
    account="Assets:YourBank:YourAccount",
    matchers=[
        ("filename", ".*0123456.*.csv"),
    ],
)

with_ledger_rules = WithHledgerRules(rules_path="hledger_rules/all.rules")

def process_extracted_entries(extracted_entries_list, ledger_entries):
    """
    Apply hooks to extracted entries.

    see https://github.com/beancount/beancount/blob/v2/examples/ingest/office/example_import.py
    """
    return [
        (filename, with_ledger_rules(entries))
        for filename, entries in extracted_entries_list
    ]

CONFIG = [
    importer_instance,
]

scripts_utils.ingest(CONFIG, filter_funcs=[process_extracted_entries])
```

## Rule Files

- rule files can either be hledger csv import rules or my own home baked yaml format.

### Hledger Rules

- see [Hledger Csv Docs](https://hledger.org/1.34/hledger.html#csv).

## Unsupported Features

- [ ] Hledger [IF Block Tables](https://hledger.org/1.34/hledger.html#if-table).
