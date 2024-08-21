export PATH := ".venv/bin:" + env_var('PATH')

default:
    @just --list

setup:
    @echo ""
    @echo "🍜 Setting up project"
    @echo ""

    pdm install

    @echo ""
    @echo "👍 Done"
    @echo ""

lint:
    echo "Linting files..."

    ruff check

    @echo ""
    @echo "👍 Done"
    @echo ""

test:
    echo "Linting files..."

    pytest

    @echo ""
    @echo "👍 Done"
    @echo ""

unittest:
    echo "Running unit tests..."

    pytest

    @echo ""
    @echo "👍 Done"
    @echo ""

integrationtest:
    echo "Running integration tests..."

    @echo ""
    @echo "👍 Done"
    @echo ""

build:
    echo "Building project..."

    pdm build

    @echo ""
    @echo "👍 Done"
    @echo ""

docs:
    echo "Generating documentation..."

    @echo ""
    @echo "👍 Done"
    @echo ""

publish TAG="next":
    echo "Publishing package..."

    @echo ""
    @echo "👍 Done"
    @echo ""
