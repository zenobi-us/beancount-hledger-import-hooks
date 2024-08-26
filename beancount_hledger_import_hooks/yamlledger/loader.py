from pathlib import Path

from pydantic_yaml import parse_yaml_file_as
from rich import print

from beancount_hledger_import_hooks.exceptions import UnknownBlockTypeError
from beancount_hledger_import_hooks.mappers import (
    IncludeRuleMapper,
    RuleSetMapper,
    TransactionRuleMapper,
)


def yamlblocks(pathname: Path) -> RuleSetMapper:
    """
    Loads a yaml file containing a list of blocks.

    Include Merging:

    When loading blocks we want to convert any
    IncludeBlockMapper into a series of TransactionBlockMapper.

    before:

        [ TransactionBlockMapper, IncludeBlockMapper, TransactionBlockMapper ]

    after:

        [ TransactionBlockMapper, TransactionBlockMapper,TransactionBlockMapper, TransactionBlockMapper ]

    """
    rule_set = parse_yaml_file_as(RuleSetMapper, pathname)

    parent = pathname.parent

    new_blocks = []

    for rule in rule_set.rules:
        if isinstance(rule, IncludeRuleMapper):
            # load the included block
            filepath = rule.value
            if not filepath:
                continue

            include_path = parent.joinpath(filepath)

            print(f"include {include_path}")

            included = yamlblocks(include_path)
            resolved_rules = [
                rule
                for rule in included.rules
                if isinstance(rule, TransactionRuleMapper)
            ]
            new_blocks.extend(resolved_rules)

        elif isinstance(rule, TransactionRuleMapper):
            new_blocks.append(rule)

        else:
            raise UnknownBlockTypeError(rule)

    return RuleSetMapper(
        rules=new_blocks,
    )
