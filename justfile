default:
    @just --list

setup:
    @echo ""
    @echo "🍜 Setting up project"
    @echo ""

    poetry install

    @echo ""
    @echo "👍 Done"
    @echo ""

lint:
    echo "Linting files..."

    ruff check

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

    poetry build

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
