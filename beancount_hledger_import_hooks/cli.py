# add current __file__ to sys.path
import sys
from pathlib import Path

import click
from rich import print

sys.path.append(str(Path(__file__).parent))

from beancount_hledger_import_hooks.hledger.loader import hledgerblocks
from beancount_hledger_import_hooks.yamlledger.loader import yamlblocks


@click.group()
def cli():
    pass


@click.group()
def hledger():
    pass


@click.command(
    name="test",
)
@click.argument("file", type=click.Path(exists=True))
def test_hledger(file: Path):
    print(f"Testing {file}")
    blocks = hledgerblocks(file)
    print(blocks)


@click.group()
def yaml():
    pass


@click.command(
    name="test",
)
@click.argument("file", type=click.Path(exists=True))
def test_yaml(file: Path):
    print(f"Testing {file}")
    blocks = yamlblocks(file)
    print(blocks)


cli.add_command(hledger)
hledger.add_command(test_hledger)
cli.add_command(yaml)
yaml.add_command(test_yaml)


if __name__ == "__main__":
    cli()
