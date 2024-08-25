from typing import Any

from beancount.core import data as beancount_data
from beancount.parser import parser
from jinja2 import Environment

from beancount_hledger_import_hooks.types import is_bean_count_transaction


class TransformBase[T]:
    def transform(self, transaction: T) -> T:
        raise NotImplementedError


def parse_plural_index(key: str, kind: str) -> int:
    """
    Parse the index from a plural key.
    """
    value = key.replace(kind, "")

    if not value:
        return 0

    return int(value)


posting_template = """
1970-01-01 * "Test"
    {value}
"""


def pasrse_posting(value: str) -> beancount_data.Posting:
    """
    Creates a fake transaction to hold our posting string.

    This allows us to parse the posting string into a beancount.core.data.Posting
    """
    fake_transaction = posting_template.format(value=value)
    entries, errors, options = parser.parse_string(fake_transaction)

    if errors:
        raise ValueError(errors)

    posting = entries[0].postings[0]

    if not isinstance(posting, beancount_data.Posting):
        raise ValueError("Expected a posting")

    return posting


def transform_account(transaction: Any, index: int, value: str) -> Any:
    """
    Transform the account field.
    """
    if not is_bean_count_transaction(transaction):
        raise ValueError("transaction must be a beancount.core.data.Transaction")

    posting = pasrse_posting(value)

    if len(transaction.postings) < index:
        transaction.postings.append(posting)
        return transaction

    transaction.postings[index] = posting

    return transaction


def transform_comment(transaction: Any, index: int, value: str) -> Any:
    """
    Transform the account field.
    """
    if not is_bean_count_transaction(transaction):
        raise ValueError("transaction must be a beancount.core.data.Transaction")

    return transaction


class Transform[T](TransformBase[T]):
    """
    A transform rule is a jinja templates.

    It is given the transaction and main account as context.
    """

    template: str
    field: str

    def __init__(self, field: str, template: str):
        self.field = field
        self.template = template

    def transform(self, transaction: Any) -> T:
        if not is_bean_count_transaction(transaction):
            raise ValueError("transaction must be a beancount.core.data.Transaction")

        env = Environment()
        template = env.from_string(self.template)
        value = template.render(Transaction=transaction)

        key = self.field.lower()

        if key.startswith("account"):
            index = parse_plural_index(key, "account")
            return transform_account(transaction, index, value)

        if key == "comment":
            index = parse_plural_index(key, "comment")
            return transform_comment(transaction, index, value)

        return transaction
