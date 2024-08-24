from typing import Any

from beancount.core.data import Amount, Posting
from jinja2 import Environment

from beancount_hledger_import_hooks.types import is_bean_count_transaction


class TransformBase[T]:
    def transform(self, transaction: T) -> T:
        raise NotImplementedError


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

        if hasattr(self, f"transform_{self.field.lower}"):
            return getattr(self, f"transform_{self.field}")(transaction, value)

        return transaction

    def transform_account2(self, transaction: Any, value: str) -> T:
        """
        Transform the account field.
        """
        if not is_bean_count_transaction(transaction):
            raise ValueError("transaction must be a beancount.core.data.Transaction")

        if len(transaction.postings) < 2:
            transaction.postings.append
            Posting(account=value, units=Amount(), cost="", price="", flag="", meta={})

        transaction.postings[1].account = value
        return transaction
