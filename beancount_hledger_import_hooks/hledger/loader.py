from pathlib import Path
from typing import Any, List

from lark import Lark, Token, Transformer
from rich import print

from beancount_hledger_import_hooks.exceptions import (
    InvalidMatchFieldKeyError,
    InvalidRuleTypeError,
    UnknownBlockTypeError,
)
from beancount_hledger_import_hooks.mappers import (
    DateFormatOptionMapper,
    IncludeRuleMapper,
    MatcherAndMapper,
    MatcherOrMapper,
    RuleSetMapper,
    TransactionRuleMapper,
    TransformMapper,
)


def transaction_field_has(field: str, value: str) -> str:
    return f'Transaction.{field.strip()} | matches "{value.strip()}"'


class HledgerTransformer(Transformer):
    def start(self, items):
        return items

    def rule(self, items):
        return items[0]

    #
    # Include Rule
    #
    def include_rule(self, include_path):
        return IncludeRuleMapper(include=include_path[0])

    def include_path(self, value):
        return str(value[0]).strip()

    #
    # Import Rule
    #
    def import_rule(self, items):
        matchers = []
        transforms = []

        for item in items:
            if isinstance(item, MatcherOrMapper) or isinstance(item, MatcherAndMapper):
                matchers.append(item)
            elif isinstance(item, TransformMapper):
                transforms.append(item)

            else:
                raise InvalidRuleTypeError(item)

        rule = TransactionRuleMapper(matchers=matchers, transforms=transforms)
        return rule

    #
    # Whole Line Match OR Rule
    def match_or_line(self, value):
        return MatcherOrMapper(or_is=transaction_field_has("narration", value[0]))

    def match_or_line_value(self, value):
        return str(value[0]).strip()

    #
    # Whole Line Match AND Rule
    def match_and_line(self, value):
        return MatcherAndMapper(and_is=transaction_field_has("narration", value[0]))

    def match_and_line_value(self, value):
        return str(value[0]).strip()

    #
    # Field Match Rule
    def match_field(self, value):
        key = value[0]
        value = value[1]
        if "or" in key:
            return MatcherOrMapper(or_is=transaction_field_has(key["or"], value))
        elif "and" in key:
            return MatcherAndMapper(and_is=transaction_field_has(key["and"], value))
        else:
            raise InvalidMatchFieldKeyError(key)

    def match_or_key(self, value):
        return {"or": value[0]}

    def match_and_key(self, value):
        return {"and": value[0]}

    def match_field_value(self, value):
        return value[0]

    #
    # Transform Rule
    def transform(self, value):
        return TransformMapper(key=value[0], value=value[1].strip())

    def transform_value(self, value: Token):
        return value[0]

    def transform_key(self, value: Token):
        return value[0]

    #
    # DateFormat option rule
    def date_format(self, value):
        return DateFormatOptionMapper(date_format=value[0])


hledger_parser = Lark.open(
    "hledger.lark",
    rel_to=__file__,
    parser="lalr",
    debug=True,
    transformer=HledgerTransformer(),
)


def parse(pathname: Path) -> RuleSetMapper:
    def load() -> Any:
        """
        Loads hledger rules files
        """
        with open(pathname, "r", encoding="utf8") as f:
            rule = f.read()
            tree = hledger_parser.parse(
                rule,
            )
            return tree

    return load()


def hledgerblocks(pathname: Path) -> RuleSetMapper:
    """
    Loads hledger rules files
    """
    new_blocks: List[
        TransactionRuleMapper | DateFormatOptionMapper | IncludeRuleMapper
    ] = []

    ruleset = parse(pathname)

    parent = pathname.parent

    for rule in ruleset:
        if isinstance(rule, DateFormatOptionMapper):
            new_blocks.append(rule)

        if isinstance(rule, IncludeRuleMapper):
            # trim any leading or trailing whitespace
            filepath = rule.value
            if not filepath:
                continue
            include_path = parent.joinpath(filepath)

            print(f"include {include_path}")

            included = hledgerblocks(include_path)

            # only include transaction rules
            # since we are resolving and flattening the rules
            rules = [
                rule
                for rule in included.rules
                if isinstance(rule, TransactionRuleMapper)
            ]

            new_blocks.extend(rules)

        elif isinstance(rule, TransactionRuleMapper):
            new_blocks.append(rule)

        else:
            raise UnknownBlockTypeError(rule)

    return RuleSetMapper(
        rules=new_blocks,
    )
