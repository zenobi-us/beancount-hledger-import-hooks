default:
    @just --list

setup:
    @echo ""
    @echo "🍜 Setting up project"
    @echo ""

    @yarn install

    @echo ""
    @echo "👍 Done"
    @echo ""

lint:
    echo "Linting files..."

    @echo ""
    @echo "👍 Done"
    @echo ""

unittest:
    echo "Running unit tests..."

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
