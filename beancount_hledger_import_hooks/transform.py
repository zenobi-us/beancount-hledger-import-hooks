from beancount.core import data as beancount_datatypes
from jinja2 import Environment


class TransformBase[T]:
    def transform(self, transaction: T) -> T:
        raise NotImplementedError


TTransaction = beancount_datatypes.Transaction


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

    def transform(self, transaction: T) -> T:
        env = Environment()
        template = env.from_string(self.template)
        value = template.render(Transaction=transaction)

        setattr(transaction, self.field, value)

        return transaction
