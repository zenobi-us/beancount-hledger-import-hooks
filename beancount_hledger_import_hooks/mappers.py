from typing import List, Union

from pydantic import BaseModel, Field


class MatcherAndMapper(BaseModel):
    value: str = Field(..., alias="and_is")


class MatcherOrMapper(BaseModel):
    value: str = Field(..., alias="or_is")


class MatcherNotMapper(BaseModel):
    value: str = Field(..., alias="is_not")


class TransformMapper(BaseModel):
    key: str
    value: str


class IncludeRuleMapper(BaseModel):
    value: str = Field(..., alias="include")


class TransactionRuleMapper(BaseModel):
    matchers: List[Union[MatcherAndMapper, MatcherOrMapper, MatcherNotMapper]]
    transforms: List[TransformMapper]


class DateFormatOptionMapper(BaseModel):
    value: str = Field(..., alias="date_format")


class RuleSetMapper(BaseModel):
    rules: List[Union[TransactionRuleMapper, IncludeRuleMapper, DateFormatOptionMapper]]
