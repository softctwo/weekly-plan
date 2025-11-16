#!/bin/bash

# Backend测试运行脚本
# Run backend tests with coverage

set -e  # Exit on error

echo "======================================"
echo "Backend Tests - Weekly Plan System"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

# Install/update dependencies
echo -e "${GREEN}Installing dependencies...${NC}"
pip install -q -r requirements.txt

echo ""
echo "======================================"
echo "Running Tests"
echo "======================================"
echo ""

# Run tests with different options based on argument
case "${1:-all}" in
    "quick")
        echo "Running quick tests (no coverage)..."
        pytest -v
        ;;
    "coverage")
        echo "Running tests with coverage report..."
        pytest --cov=app --cov-report=html --cov-report=term-missing
        echo ""
        echo -e "${GREEN}Coverage report generated in htmlcov/index.html${NC}"
        ;;
    "api")
        echo "Running API tests only..."
        pytest -v -m api
        ;;
    "model")
        echo "Running model tests only..."
        pytest -v -m model
        ;;
    "unit")
        echo "Running unit tests only..."
        pytest -v -m unit
        ;;
    "verbose")
        echo "Running tests with maximum verbosity..."
        pytest -vv --tb=long
        ;;
    *)
        echo "Running all tests with coverage..."
        pytest --cov=app --cov-report=html --cov-report=term-missing
        echo ""
        echo -e "${GREEN}✓ All tests completed!${NC}"
        echo -e "${GREEN}Coverage report: htmlcov/index.html${NC}"
        ;;
esac

# Exit code from pytest
TEST_EXIT_CODE=$?

echo ""
echo "======================================"
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ Tests passed successfully!${NC}"
else
    echo -e "${RED}✗ Some tests failed. Check output above.${NC}"
fi
echo "======================================"

exit $TEST_EXIT_CODE
