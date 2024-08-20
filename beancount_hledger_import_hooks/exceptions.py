from typing import Any


class UnknownBlockTypeError(Exception):
    def __init__(self, block: Any):
        self.message = f"Unknown block type: {block}"
        super().__init__(self.message)

    def __str__(self):
        return self.message


class InvalidMatchFieldKeyError(Exception):
    def __init__(self, key: Any):
        self.message = f"Invalid match field key: {key}"
        super().__init__(self.message)

    def __str__(self):
        return self.message


class InvalidRuleTypeError(Exception):
    def __init__(self, item: Any):
        self.message = f"Invalid rule type: {item}"
        super().__init__(self.message)

    def __str__(self):
        return self.message
