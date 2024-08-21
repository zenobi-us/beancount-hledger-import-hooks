from beancount_hledger_import_hooks.interrogator import JinjaInterrogator


def test_jinja_interrogator():
    interrogator = JinjaInterrogator()

    assert interrogator("Transaction.foo == 1", {"foo": 1})
    assert not interrogator("Transaction.foo == 2", {"foo": 1})
    assert interrogator(
        "Transaction.foo.bar.baz.endswith('kaboom')",
        {"foo": {"bar": {"baz": "kaboom"}}},
    )

    assert interrogator("'bar' in Transaction|values|join(' ')", {"foo": "bar"})
    assert not interrogator("'baz' in Transaction|values|join(' ')", {"foo": "bar"})
    assert interrogator("'foo' in Transaction|keys|join(' ')", {"foo": "bar"})
