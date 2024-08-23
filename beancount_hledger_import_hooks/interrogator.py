from typing import NamedTuple

from jinja2 import Environment


class InterrogatorBase[T]:
    """
    An interrogator is a class that can be
    called with a source string and a context.

    The interrogator will return a boolean value.
    """

    def __call__(self, source: str, context: T) -> bool:
        raise NotImplementedError


class JinjaInterrogator(InterrogatorBase[dict]):
    """
    A JinjaInterrogator is a class that stores context and executes a [jinja](https://jinja.palletsprojects.com/en/3.1.x/) expression.

    The provided expression is executed with [Environment.compile_expression](https://jinja.palletsprojects.com/en/3.1.x/api/#jinja2.Environment.compile_expression).

    The context is a dictionary that will be assigned to the variable `Transaction` and used to evaluate the template.

    Example:

    >>> interrogator = JinjaInterrogator(
    ...     context={"Description": "foo"}
    ... )
    >>>
    >>> interrogator("Description == 'foo'")
    True
    >>> interrogator("'fo' in Description")
    True
    >>> interrogator("Description.endswith('oo')")
    True
    >>> interrogator("Description.endswith('bar')")
    False
    >>> interrogator("Description == 'bar'")
    False
    >>> interrogator("'bar' in Description")
    False
    >>> interrogator("foo")
    # treated as `'foo' in Transaction|values|join(' ')`
    True

    More Information:

    see [https://jinja.palletsprojects.com/en/3.0.x/templates/#expressions](https://jinja.palletsprojects.com/en/3.0.x/templates/#expressions)

    """

    context: dict

    def __init__(self, context: dict | None = None):
        self.env = Environment()
        self.context = context or {}

        self.env.filters["keys"] = self.filter_get_dict_keys
        self.env.filters["values"] = self.filter_get_dict_values

    def filter_get_dict_keys(self, x: dict):
        return x.keys()

    def filter_get_dict_values(self, x: dict):
        return x.values()

    def __call__(self, source: str, context: NamedTuple):
        template = self.env.compile_expression(source)
        merged_context = {**self.context, **context._asdict()}
        result = template(Transaction=merged_context)

        return result
