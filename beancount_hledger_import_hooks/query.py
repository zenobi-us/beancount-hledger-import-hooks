"""
This module contains a set of fluent apis for chaining Or, And, Not operations.

The result is based on input context and the provided rule(s).

Usage example:


    >>> from query import OrQuery, AndQuery, NotQuery
    >>>
    >>> result = Query(
    ...     context=transactions,
    ...     query=OrQuery(
    ...         OrQuery("description.is('foo')", "description.is('bar')"),
    ...         AndQuery(
    ...             OrQuery("description.is('foo')", "description.is('bar')"),
    ...             NotQuery("description.is('baz')")
    ...         ),
    ...         NotQuery("description.is('baz')")
    ...     )
    ... )
    >>>
    >>> print(result === True)
    ),
"""


class QueryBase[TContext]:
    """
    A query can be a string or on or more query objects.
    """

    def satisfies(self, context: TContext) -> bool:
        raise NotImplementedError


class OrQuery[TContext](QueryBase[TContext]):
    def __init__(self, *queries: QueryBase):
        self.queries = queries

    def satisfies(self, context: TContext) -> bool:
        return any(query.satisfies(context) for query in self.queries)


class AndQuery[TContext](QueryBase[TContext]):
    def __init__(self, *queries: QueryBase):
        self.queries = queries

    def satisfies(self, context: TContext) -> bool:
        return all(query.satisfies(context) for query in self.queries)


class NotQuery[TContext](QueryBase[TContext]):
    def __init__(self, *queries: QueryBase):
        self.queries = queries

    def satisfies(self, context: TContext) -> bool:
        return not any(query.satisfies(context) for query in self.queries)


class Query[TContext](QueryBase[TContext]):
    def __init__(self, context: TContext, query: QueryBase):
        self.context = context
        self.query = query

    def satisfies(self) -> bool:
        return self.query.satisfies(self.context)
