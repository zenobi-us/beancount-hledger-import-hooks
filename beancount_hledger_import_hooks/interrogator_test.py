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


def test_jinja_custom_regex_filter():
    new_entries, _, __ = loader.load_string("""
        2016-01-06 * "VISA DEBIT WOOLWORTHS 1234"
            Expenses:Groceries    1.06 USD
    """)
    interrogator = JinjaInterrogator()

    assert interrogator("Transaction.narration|search('WOOLWORTHS')", new_entries[0])
    assert interrogator("Transaction.narration|search('WOOL.*') ", new_entries[0])
    assert interrogator("Transaction.narration|search('\d+') ", new_entries[0])
    assert interrogator(
        "Transaction.narration|matches('VISA .* 1234') ", new_entries[0]
    )


def test_jinja_custom_date_filter():
    new_entries, _, __ = loader.load_string("""
        2016-01-06 * "VISA DEBIT WOOLWORTHS 1234"
            Expenses:Groceries    1.06 USD
    """)
    interrogator = JinjaInterrogator()

    assert interrogator("Transaction.date|date == '06/01/2016'", new_entries[0])


def test_jinja_custom_glob_filter():
    new_entries, _, __ = loader.load_string("""
        2016-01-06 * "VISA DEBIT WOOLWORTHS 1234"
            Expenses:Groceries    1.06 USD
    """)
    interrogator = JinjaInterrogator()

    assert interrogator("Transaction.date == '06/01/2016'", new_entries[0])
    assert interrogator("Transaction.date|search('06/01/2016')", new_entries[0])
