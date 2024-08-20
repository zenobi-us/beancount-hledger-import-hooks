from typing import Any, List, Union

from beancount_hledger_import_hooks import mappers


class MatcherBase[T]:
    def satisfies(self, transaction: T) -> bool:
        raise NotImplementedError


class MatcherSetBase[T](MatcherBase[T]):
    pass


class MatcherTemplate[T](MatcherBase[T]):
    template: str = ""

    def __init__(self, template: str) -> None:
        self.template = template

    def satisfies(self, transaction: T) -> bool:
        raise NotImplementedError


class MatcherAnd[T](MatcherSetBase[T]):
    And: List[MatcherTemplate[T]] = []

    def __init__(self, mapper: mappers.MatcherAndMapper) -> None:
        rules = [MatcherTemplate(template) for template in mapper.value]

        self.And = rules

    def satisfies(self, transaction: T) -> bool:
        return all(m.satisfies(transaction) for m in self.And)


class MatcherOr[T](MatcherSetBase[T]):
    Or: List[MatcherTemplate[T]] = []

    def __init__(self, mapper: mappers.MatcherOrMapper) -> None:
        rules = [MatcherTemplate(template) for template in mapper.value]

        self.Or = rules

    def satisfies(self, transaction: T) -> bool:
        return any(m.satisfies(transaction) for m in self.Or)


class MatcherNot[T](MatcherSetBase[T]):
    Not: List[MatcherTemplate[T]] = []

    def __init__(self, mapper: mappers.MatcherNotMapper) -> None:
        rules = [MatcherTemplate(template) for template in mapper.value]

        self.Not = rules

    def satisfies(self, transaction: T) -> bool:
        return not any(m.satisfies(transaction) for m in self.Not)


type Matcher[T] = Union[MatcherAnd[T], MatcherOr[T], MatcherNot[T]]


def resolve_matcher_type[T](
    mapper: Union[
        mappers.MatcherAndMapper[T],
        mappers.MatcherOrMapper[T],
        mappers.MatcherNotMapper[T],
        Any,
    ],
) -> Matcher[T]:
    if isinstance(mapper, mappers.MatcherAndMapper[T]):
        return MatcherAnd[T](mapper)

    if isinstance(mapper, mappers.MatcherOrMapper[T]):
        return MatcherOr[T](mapper)

    if isinstance(mapper, mappers.MatcherNotMapper[T]):
        return MatcherNot[T](mapper)

    raise ValueError(f"Unknown matcher type: {mapper}")
