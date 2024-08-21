from typing import List

from beancount_hledger_import_hooks.interrogator import InterrogatorBase
from beancount_hledger_import_hooks.mappers import (
    IncludeRuleMapper,
    MatcherAndMapper,
    MatcherNotMapper,
    MatcherOrMapper,
    RuleSetMapper,
    TransactionRuleMapper,
)
from beancount_hledger_import_hooks.matchers import (
    Matcher,
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

    interrogator: InterrogatorBase[T]

    def __init__(self, mapper: TransactionRuleMapper[T] | IncludeRuleMapper[T]):
        """
        Create a transformer from a block
        """
        if isinstance(mapper, IncludeRuleMapper[T]):
            raise ValueError("IncludeBlockMapper is not supported")

        matchers: List[Matcher] = []
        for matcher in mapper.matchers:
            if isinstance(matcher, MatcherAndMapper[T]):
                matchers.append(
                    Matcher(
                        matcher.value,
                        kind="And",
                    )
                )

            if isinstance(matcher, MatcherOrMapper[T]):
                matchers.append(
                    Matcher(
                        matcher.value,
                        kind="Or",
                    )
                )

            if isinstance(matcher, MatcherNotMapper[T]):
                matchers.append(
                    Matcher(
                        matcher.value,
                        kind="Not",
                    )
                )

        self.matcher = Matcher(
            *matchers,
            kind="And",
        )

        # for transform in mapper.transforms:
        #     self.transforms.append(TransformRule.parse_obj(transform))

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


class RuleSet[T]:
    rules: List[Rule[T]] = []

    def __init__(self, ruleset: RuleSetMapper):
        """
        Create a transformer set from a block set
        """
        for rule in ruleset.rules:
            self.rules.append(Rule(rule))

    def run(self, transactions: List[T]) -> List[T]:
        """
        Run the transformers on the transactions
        """
        for transaction in transactions:
            for rule in self.rules:
                transaction = rule.process(transaction)

        return transactions
