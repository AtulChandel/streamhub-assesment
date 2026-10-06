#!/usr/bin/env bash
set -e

echo "================================================================================"
echo "          STREAMHUB ASSESSMENT AUTOMATED EXECUTION SUITE (PYTHON)               "
echo "================================================================================"

# Activate virtual environment if present
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Ensure output directories exist
mkdir -p reports/screenshots sql/results

echo ""
echo "[1/4] Ensuring StreamEMI Web Application is active on port 5001..."
if ! curl -s http://127.0.0.1:5001/api/health > /dev/null 2>&1; then
    echo "Starting Flask web application in background..."
    python3 web_app/app.py > /dev/null 2>&1 &
    FLASK_PID=$!
    sleep 2
    echo "Web application running (PID: $FLASK_PID)."
else
    echo "Web application is already running and healthy."
fi

echo ""
echo "[2/4] Running Playwright E2E UI Tests (A2)..."
pytest tests/e2e/test_emi_calculator.py --html=reports/e2e_report.html --self-contained-html

echo ""
echo "[3/4] Running Playwright API Boundary Tests on JSONPlaceholder (A3)..."
pytest tests/api/test_posts_boundary.py --html=reports/api_report.html --self-contained-html

echo ""
echo "[4/4] Executing SQL Tests & Generating Visual Screenshot Evidence (A4)..."
python3 sql/execute_sql_tests.py

echo ""
echo "================================================================================"
echo "                    ALL ASSESSMENT SUITES COMPLETED                             "
echo "================================================================================"
echo "Artifacts generated:"
echo "  - E2E Test Report:      reports/e2e_report.html"
echo "  - API Test Report:      reports/api_report.html"
echo "  - SQL Results Report:   reports/sql_results.html"
echo "  - Test Screenshots:     reports/screenshots/"
echo "  - SQL Text Results:     sql/results/"
echo "================================================================================"
