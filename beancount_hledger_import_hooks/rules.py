from typing import List, Union

from beancount_hledger_import_hooks.interrogator import InterrogatorBase
from beancount_hledger_import_hooks.mappers import (
    DateFormatOptionMapper,
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
    ):
        """
        Create a transformer from a block
        """
        self.matcher = matcher
        self.transforms = transforms

    def satisfies(self, transaction: T, interrogator: InterrogatorBase) -> bool:
        """
        Test if any of the matchers match the transaction
        """
        result = ResolveQuery(
            transaction,
            interrogator,
            self.matcher,
        )

        return result

    def transform(self, transaction: T):
        """
        Transform a transaction into a ledger entry
        """
        for rule in self.transforms:
            # accumulate the output
            transaction = rule.transform(transaction)

        return transaction

    def process(self, transaction: T, interrogator: InterrogatorBase) -> T:
        """
        Process the transaction
        """
        if self.satisfies(transaction, interrogator):
            return self.transform(transaction)

        return transaction

    @classmethod
    def from_mapper[F](
        cls,
        matchers: List[Union[MatcherAndMapper, MatcherOrMapper, MatcherNotMapper]],
        transforms: List[TransformMapper],
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
        )


class RuleSetOptions:
    """
    Options for a rule set
    """

    date_format: str = "%d/%m/%Y"

    def __init__(self):
        pass


class RuleSet[T]:
    rules: List[Rule[T]] = []
    options: RuleSetOptions = RuleSetOptions()

    def __init__(self, rules: List[Rule[T]], options: RuleSetOptions | None = None):
        """
        Create a transformer set from a block set
        """
        self.rules = rules
        self.options = options or RuleSetOptions()

    def run(self, transactions: List[T], interrogator: InterrogatorBase) -> List[T]:
        """
        Run the transformers on the transactions
        """
        for transaction in transactions:
            for rule in self.rules:
                transaction = rule.process(transaction, interrogator)

        return transactions

    @classmethod
    def from_mapper[F](cls, mapper: RuleSetMapper) -> "RuleSet[F]":  # type: ignore
        rules: List[Rule[F]] = []
        options: RuleSetOptions = RuleSetOptions()

        for rule in mapper.rules:
            if isinstance(rule, DateFormatOptionMapper):
                options.date_format = rule.value

            if isinstance(rule, TransactionRuleMapper):
                rules.append(
                    Rule.from_mapper(
                        rule.matchers,
                        rule.transforms,
                    )
                )

        return RuleSet[F](rules=rules, options=options)
