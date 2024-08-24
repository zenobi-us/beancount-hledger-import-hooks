from beancount import loader

from beancount_hledger_import_hooks.interrogator import JinjaInterrogator


def test_jinja_interrogator():
    new_entries, _, __ = loader.load_string("""
        2016-01-06 *
            Expenses:Groceries    1.06 USD
    """)
    interrogator = JinjaInterrogator()

    assert interrogator("'payee' in Transaction|keys|join(' ')", new_entries[0])
    assert interrogator(
        "Transaction.postings.0.units.number|float == 1.06", new_entries[0]
    )
