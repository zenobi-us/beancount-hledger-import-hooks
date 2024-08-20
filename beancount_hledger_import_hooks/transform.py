class TransformBase[T]:
    def transform(self, transaction: T) -> T:
        raise NotImplementedError


class Transform[T](TransformBase[T]):
    """
    A transform rule is a jinja templates.

    It is given the transaction and main account as context.
    """

    def __init__(self, mapper: str):
        self.template = mapper
