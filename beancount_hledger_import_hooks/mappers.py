from typing import List, Union

from pydantic import BaseModel, Field


class MatcherAndMapper(BaseModel):
    value: str = Field(..., alias="and_is")


class MatcherOrMapper(BaseModel):
    value: str = Field(..., alias="or_is")


class MatcherNotMapper(BaseModel):
    value: str = Field(..., alias="is_not")


def matcher_command(operator: str, key: str, value: str) -> str:
    return f'{key}.{operator}("{value.strip()}")'


def matcher_command_has(key: str, value: str) -> str:
    return matcher_command("has", key, value)


class TransformSetMapper(BaseModel):
    value: str = Field(..., alias="set_to")


def transform_command(operator: str, key: str, value: str) -> str:
    return f'{key}.{operator}("{value.strip()}")'


def transform_command_set(key: str, value: str) -> str:
    return transform_command("set", key, value)


class IncludeRuleMapper(BaseModel):
    value: str = Field(..., alias="include")


class TransactionRuleMapper(BaseModel):
    matchers: List[Union[MatcherAndMapper, MatcherOrMapper, MatcherNotMapper]]
    transforms: List[TransformSetMapper]


class RuleSetMapper(BaseModel):
    rules: List[Union[TransactionRuleMapper, IncludeRuleMapper]]
