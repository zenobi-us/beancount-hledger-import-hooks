from typing import Any, Literal

from beancount_hledger_import_hooks.interrogator import InterrogatorBase


class Matcher:
    """
    A match is a class that can be used to match a transaction

    it has a kind, which can be a string that is one of:
    - And
    - Or
    - Not

    it has a collection of items, which can be a list of matchers
    """

    kind: Literal["And", "Or", "Not"]
    items: list["Matcher | str"]

    def __init__(self, *items: "Matcher | str", kind: Literal["And", "Or", "Not"]):
        self.kind = kind
        self.items = list(items)


class OrMatcher(Matcher):
    def __init__(self, *items: "Matcher | str"):
        super().__init__(*items, kind="Or")


class AndMatcher(Matcher):
    def __init__(self, *items: "Matcher | str"):
        super().__init__(*items, kind="And")


class NotMatcher(Matcher):
    def __init__(self, *items: "Matcher | str"):
        super().__init__(*items, kind="Not")


def ResolveQuery(
    transaction: Any,
    interrogator: InterrogatorBase,
    query: Matcher | str,
) -> bool:
    """
    Resolve a query against a transaction.

    Args:
        query: The query to resolve
        transaction: The transaction to resolve against
        interrogator: A function that will resolve the transaction
    """
    if isinstance(query, str):
        result = interrogator(query, transaction)
        return result

    if query.kind == "And":
        """
        An And matcher will ensure that all of the items are truthy.

        if one item is falsy, then the result will be false
        """
        results = []
        for m in query.items:
            result = ResolveQuery(transaction, interrogator, m)
            results.append(result)

        result = all(results)

        return result

    if query.kind == "Or":
        """
        An Or matcher will ensure that at least one of the items is truthy.

        if one item is truthy, then the result will be true
        """
        results = []
        for m in query.items:
            result = ResolveQuery(transaction, interrogator, m)
            results.append(result)

        result = any(results)

        return result

    if query.kind == "Not":
        """
        A Not matcher will ensure that none of the items are truthy.

        if one item is truthy, then the result will be false
        """
        for m in query.items:
            result = ResolveQuery(transaction, interrogator, m)
            if result:
                return False

        return True

    return False
