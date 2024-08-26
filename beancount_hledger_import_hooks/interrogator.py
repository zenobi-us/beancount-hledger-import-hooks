import datetime
import fnmatch
import re
from ast import Dict
from typing import Any

from jinja2 import Environment, Undefined


class InterrogatorBase:
    """
    An interrogator is a class that can be
    called with a source string and a context.

    The interrogator will return a boolean value.
    """

    date_format: str

    def __call__(self, source: str, context: Any) -> bool:
        raise NotImplementedError

    def context_accessor(self, transaction: Any) -> Dict:
        """
        Transform a transaction into a dictionary.

        recursively transform the transaction into a dictionary.

        any datetime objects are converted to strings using the date_format.
        """
        output = transaction._asdict()

        def walk_dict(d):
            for key, value in d.items():
                if isinstance(value, datetime.datetime):
                    d[key] = value.strftime(self.date_format)
                    continue

                if isinstance(value, datetime.date):
                    d[key] = value.strftime(self.date_format)
                    continue

                if isinstance(value, dict):
                    d[key] = walk_dict(value)
                    continue

            return d

        result = walk_dict(output)

        return result


class JinjaInterrogator(InterrogatorBase):
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

    def __init__(self, date_format: str = "%d/%m/%Y", context: Dict | None = None):
        self.env = Environment()

        self.env.filters["keys"] = self.filter_get_dict_keys
        self.env.filters["values"] = self.filter_get_dict_values
        # searching
        self.env.filters["matches"] = self.filter_regex_match
        self.env.filters["search"] = self.filter_regex_search
        self.env.filters["regex_match"] = self.filter_regex_match
        self.env.filters["regex_search"] = self.filter_regex_match
        self.env.filters["glob_match"] = self.filter_glob_match
        self.env.tests["matches"] = self.test_regex_match
        self.env.tests["search"] = self.test_regex_search
        self.env.tests["regex_match"] = self.test_regex_match
        self.env.tests["regex_search"] = self.test_regex_search
        self.env.tests["glob_match"] = self.test_glob_match
        # date formatting
        self.env.filters["isodate"] = self.filter_isodate
        self.env.filters["isodatetime"] = self.filter_isodatetime
        self.env.filters["isotime"] = self.filter_isotime
        self.env.filters["dateformat"] = self.filter_dateformat
        self.env.filters["date"] = self.filter_date

        self.date_format = date_format

    def date_to_str(self, x: Any):
        if isinstance(x, datetime.datetime):
            return x.strftime(self.date_format)

        return x

    def filter_get_dict_keys(self, x: dict | None):
        if x is None:
            return []
        return x.keys()

    def filter_get_dict_values(self, x: dict | None):
        if x is None:
            return []
        return [self.date_to_str(value) for value in x.values()]

    def filter_isodate(self, x: datetime.date | None | str):
        if x is None:
            return ""
        if isinstance(x, datetime.date):
            return x.strftime("%Y-%m-%d")
        return x

    def filter_isodatetime(self, x: datetime.datetime | None | str):
        if x is None:
            return ""
        if isinstance(x, datetime.datetime):
            return x.strftime("%Y-%m-%dT%H:%M:%S")
        return x

    def filter_isotime(self, x: datetime.datetime | None | str):
        if x is None:
            return ""
        if isinstance(x, datetime.datetime):
            return x.strftime("%H:%M:%S")
        return x

    def filter_dateformat(
        self, x: datetime.datetime | datetime.date | None | str, format: str
    ):
        if x is None:
            return ""
        if isinstance(x, datetime.datetime) or isinstance(x, datetime.date):
            return x.strftime(self.date_format)
        return x

    def filter_date(self, x: datetime.datetime | datetime.date | None | str):
        if x is None:
            return ""
        if isinstance(x, datetime.datetime) or isinstance(x, datetime.date):
            return x.strftime(self.date_format)
        return x

    def filter_regex_match(self, value: str | None, pattern: str):
        if value is None or value == "Undefined":
            return False
        return bool(re.match(pattern, self.date_to_str(value)))

    def filter_regex_search(self, value: str | None, pattern: str):
        if value is None or value == "Undefined" or isinstance(value, Undefined):
            return False
        return bool(re.search(pattern, self.date_to_str(value)))

    def filter_glob_match(self, value: str | None, pattern: str):
        if value is None or value == "Undefined":
            return False
        return bool(fnmatch.fnmatch(self.date_to_str(value), pattern))

    def test_regex_match(self, value: str | None, pattern: str):
        if value is None or value == "Undefined":
            return False
        return bool(re.match(pattern, self.date_to_str(value)))

    def test_regex_search(self, value: str | None, pattern: str):
        if value is None or value == "Undefined":
            return False
        return bool(re.search(pattern, self.date_to_str(value)))

    def test_glob_match(self, value: str | None, pattern: str):
        if value is None or value == "Undefined":
            return False
        return bool(fnmatch.fnmatch(self.date_to_str(value), pattern))

    def __call__(self, source: str, transaction: Any):
        try:
            template = self.env.compile_expression(source)
        except Exception:
            raise InterrogatorExpressionError(f"Error evaluating expression: {source}")

        try:
            merged_context = self.context_accessor(transaction)
        except Exception:
            raise InterrogatorContextMergeError(f"Error merging context: {transaction}")

        try:
            result = template(Transaction=merged_context)
        except Exception:
            raise InterrogatorEvaluateExpressionError(
                f"Error evaluating expression: {source}"
            )

        return result

    @classmethod
    def create_default_expression(cls, field: str, value: str) -> str:
        return f'Transaction.{field.strip()}|search("{value.strip()}")'


class InterrogatorExpressionError(Exception):
    pass


class InterrogatorContextMergeError(Exception):
    pass


class InterrogatorEvaluateExpressionError(Exception):
    pass
