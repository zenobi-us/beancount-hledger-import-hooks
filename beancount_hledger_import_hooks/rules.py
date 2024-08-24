from typing import List, Union

from beancount_hledger_import_hooks.interrogator import InterrogatorBase
from beancount_hledger_import_hooks.mappers import (
    MatcherAndMapper,
    MatcherNotMapper,
    MatcherOrMapper,
    RuleSetMapper,
    TransactionRuleMapper,
    TransformMapper,
)
from beancount_hledger_import_hooks.matchers import (
    AndMatcher,
    Matcher,
    NotMatcher,
    OrMatcher,
    ResolveQuery,
)
from beancount_hledger_import_hooks.transform import Transform


class Rule[T]:
    """
    A transform block can look like

        - name: Some name
        matchers:
        - And:
            - Transaction.Description.includes("Debit")
            - Transaction.Description.includes("Wholefoods")
        - Or:
            - Transaction.Description.includes("Groceries")
            - Transaction.Amount > 100
        transforms:
        - Expenses:Food:Groceries  {{ Transaction.Amount }}

    It describes:
    - a name
    - a list of matchers. if any match, then the transforms are applied
    - a list of transforms to apply
    """

    matcher: Matcher

    transforms: List[Transform[T]] = []

    interrogator: InterrogatorBase

    def __init__(
        self,
        matcher: Matcher,
        transforms: List[Transform[T]],
        interrogator: InterrogatorBase,
    ):
        """
        Create a transformer from a block
        """
        self.matcher = matcher
        self.transforms = transforms
        self.interrogator = interrogator

    def satisfies(self, transaction: T) -> bool:
        """
        Test if any of the matchers match the transaction
        """
        return ResolveQuery(
            transaction,
            self.interrogator,
            self.matcher,
        )

    def transform(self, transaction: T):
        """
        Transform a transaction into a ledger entry
        """
        for rule in self.transforms:
            # accumulate the output
            transaction = rule.transform(transaction)

        return transaction

    def process(self, transaction: T) -> T:
        """
        Process the transaction
        """
        if self.satisfies(transaction):
            return self.transform(transaction)

        return transaction

    @classmethod
    def from_mapper[F](
        cls,
        matchers: List[Union[MatcherAndMapper, MatcherOrMapper, MatcherNotMapper]],
        transforms: List[TransformMapper],
        interrogator: InterrogatorBase,
    ) -> "Rule[F]":  # type: ignore
        mapped_matchers: List[Matcher] = []
        mapped_transforms: List[Transform[F]] = []

        for matcher in matchers:
            if isinstance(matcher, MatcherAndMapper):
                mapped_matchers.append(
                    AndMatcher(
                        matcher.value,
                    )
                )

            if isinstance(matcher, MatcherOrMapper):
                mapped_matchers.append(
                    OrMatcher(
                        matcher.value,
                    )
                )

            if isinstance(matcher, MatcherNotMapper):
                mapped_matchers.append(
                    NotMatcher(
                        matcher.value,
                    )
                )

        for transform in transforms:
            mapped_transforms.append(
                Transform(field=transform.key, template=transform.value)
            )

        return Rule[F](
            matcher=OrMatcher(
                *mapped_matchers,
            ),
            transforms=mapped_transforms,
            interrogator=interrogator,
        )


class RuleSet[T]:
    rules: List[Rule[T]] = []

    def __init__(self, rules: List[Rule[T]]):
        """
        Create a transformer set from a block set
        """
        self.rules = rules

    def run(self, transactions: List[T]) -> List[T]:
        """
        Run the transformers on the transactions
        """
        for transaction in transactions:
            for rule in self.rules:
                transaction = rule.process(transaction)

        return transactions

    @classmethod
    def from_mapper[F](
        cls, mapper: RuleSetMapper, interrogator: InterrogatorBase
    ) -> "RuleSet[F]":  # type: ignore
        rules: List[Rule[F]] = []

        for rule in mapper.rules:
            if isinstance(rule, TransactionRuleMapper):
                rules.append(
                    Rule.from_mapper(
                        rule.matchers,
                        rule.transforms,
                        interrogator=interrogator,
                    )
                )

        return RuleSet[F](rules=rules)
