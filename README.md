# Streamhub Technical Assessment — Complete Solution Suite

A production-grade implementation of all four assessment modules built entirely in **Python**, featuring an interactive web application, Playwright end-to-end automation, Playwright API boundary testing, and advanced SQL analytical queries.

---

## 📑 Project Structure

```
streamhub-assessment/
├── web_app/                               # [A1] Python Web Application
│   ├── app.py                             # Flask backend & REST calculation endpoints
│   ├── templates/
│   │   └── index.html                     # Responsive loan analytics dashboard
│   └── static/
│       ├── css/style.css                  # Curated dark-theme design system
│       └── js/calculator.js               # Reactive dual-sync controls & visual SVG donut chart
├── tests/
│   ├── e2e/                               # [A2] Playwright UI Automation
│   │   ├── pages/
│   │   │   └── emi_calculator_page.py     # Page Object Model (POM) implementation
│   │   └── test_emi_calculator.py         # End-to-end test scenarios
│   ├── api/                               # [A3] Playwright API Automation
│   │   └── test_posts_boundary.py         # JSONPlaceholder boundary & invalid data tests
│   ├── utils/
│   │   ├── emi_math.py                    # Independent financial math computation engine
│   │   └── dynamic_locators.py            # Dynamic, parameterized locator factory
│   └── config/
│       └── environment.py                 # Multi-environment config (LOCAL, STAGING, PROD)
├── sql/                                   # [A4] SQL Analytical Queries
│   ├── scenario1_roundtrip_transfers.sql  # Round-trip transfers (24h / 10% tolerance)
│   ├── scenario2_ipl_streaks.sql          # IPL 2024 streaks (Island-and-Gaps pattern)
│   ├── execute_sql_tests.py               # Automated SQL execution & screenshot generator
│   └── results/                           # Text-based query outputs
├── reports/
│   ├── e2e_report.html                    # Playwright E2E HTML execution report
│   ├── api_report.html                    # Playwright API HTML execution report
│   ├── sql_results.html                   # SQL query output visual report
│   └── screenshots/                       # High-resolution screenshots of UI & SQL results
├── run_assessment.sh                      # One-click execution script for all test suites
├── requirements.txt                       # Python dependencies
└── pytest.ini                             # Pytest test discovery & runner configuration
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+
- macOS / Linux / Windows

### 2. Environment Setup
```bash
# 1. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate       # On Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install Playwright browser binaries
playwright install chromium
```

### 3. Run Everything with One Command
```bash
./run_assessment.sh
```

---

## 📊 Module Breakdown & Technical Deliverables

### A1. Web Application: StreamEMI Loan & Mortgage Analytics
- **Live Local Server**: `python web_app/app.py` (served on `http://127.0.0.1:5001`).
- **Core Capabilities**:
  1. **Dual-Sync Interactive Controls**: Real-time two-way synchronized numeric input boxes and range sliders for Loan Amount, Interest Rate, and Tenure.
  2. **Tenure Toggle**: Seamlessly switch between Years and Months.
  3. **Multi-Currency Support**: Dynamic currency switching across `$ (USD)`, `₹ (INR)`, `€ (EUR)`, and `£ (GBP)`.
  4. **Visual Element (SVG Donut Chart)**: Dynamic vector donut chart displaying exact proportions of Principal vs. Total Interest with center summary.
  5. **Amortization Report**: Period-by-period payment table displaying Opening Balance, EMI Paid, Principal Component, Interest Component, Closing Balance, and % Loan Repaid. Supports **Yearly/Monthly view toggle**, **live search/filtering**, and **Export to CSV**.
  6. **Aesthetics**: Glassmorphism cards, Inter & JetBrains Mono typography, vibrant dark mode palette, and glowing micro-interactions.

---

### A2. Playwright E2E Test Automation
- **Framework Architecture**:
  - **Page Object Model (`tests/e2e/pages/emi_calculator_page.py`)**: Strict encapsulation of all page interactions, inputs, and element queries.
  - **Dynamic Locators (`tests/utils/dynamic_locators.py`)**: Parameterized locator factories (`metric_card(key)`, `numeric_input(field)`, `range_slider(field)`, `schedule_row(period)`).
  - **Environment Configuration (`tests/config/environment.py`)**: Configurable environments (`LOCAL`, `STAGING`, `PROD`) with timeout and URL management.
  - **Independent Math Engine (`tests/utils/emi_math.py`)**: Computes exact financial annuity equations independently from the application under test:
    $$\text{EMI} = P \times \frac{r(1+r)^n}{(1+r)^n - 1}$$
- **Test Scenarios Covered (`tests/e2e/test_emi_calculator.py`)**:
  - `test_dashboard_loads_successfully`: Verifies page title, branding, input controls, metric cards, visual chart, and report tables.
  - `test_default_values_match_independent_computation`: Independently verifies default $1M @ 8.5% for 20 years ($8,678.23 monthly EMI, $1,082,775.76 interest).
  - `test_user_input_submission_and_dynamic_calculation`: Submits varied user inputs across multiple loan types (Auto loan, Mid-term mortgage, Commercial loan, Short tenure in months) and verifies exact mathematical correctness against independent math.
  - `test_visual_chart_renders_non_zero_valid_data`: Verifies SVG donut chart visibility, verifies stroke-dasharray values are non-zero, sums to circumference, and center label displays total loan value.
  - `test_amortization_schedule_table_rows_and_filtering`: Tests yearly row counts, monthly view toggle (240 rows), interactive row filtering, and 100% repayment completion.
- **Run E2E Tests**:
  ```bash
  pytest tests/e2e/test_emi_calculator.py --html=reports/e2e_report.html --self-contained-html
  ```

---

### A3. Playwright API Boundary & Resilience Testing
- **Target Endpoint**: `POST https://jsonplaceholder.typicode.com/posts`
- **Client**: Playwright's `APIRequestContext` (`tests/api/test_posts_boundary.py`).
- **Test Scenarios Covered**:
  1. **Excessively Long Strings**: 5,000, 25,000, and 50,000 character titles sent to test buffer management.
  2. **Unsupported Special Characters & Injection Attacks**:
     - XSS script tags: `<script>alert('STREAMHUB_SEC_AUDIT')</script><img src=x onerror=alert(1)>`
     - SQL Injection: `'; DROP TABLE posts; SELECT * FROM users WHERE '1'='1'--`
     - Unicode & Emojis: `🔥✨🚀🛡️💯 𝕽𝖊𝖘𝖎𝖑𝖎𝖊𝖓𝖈𝖊 測試 テスト اختبار`
     - Bi-directional RTL control characters: `\u202E\u200F\u202B...`
     - Null byte injection: `prefix_text\x00suffix_hidden_payload`
  3. **Missing Required Fields**:
     - Missing `userId`
     - Missing `title`
     - Missing `body`
     - Completely empty JSON payload `{}`
     - Null fields `{"title": None, "body": None, "userId": None}`
  4. **Boundary Field Data Types**: String `userId`, negative `userId` (-9999), 64-bit integer overflow, float `userId`.
  5. **Resilience & Contract Verification**: Server maintains 100% uptime with no 5xx unhandled exceptions; validates payload preservation and JSON mock contract behavior.
- **Run API Tests**:
  ```bash
  pytest tests/api/test_posts_boundary.py --html=reports/api_report.html --self-contained-html -s
  ```

---

### A4. SQL Tests

#### Scenario 1: Round-Trip Money Transfers
**Objective**: Identify transfers where Account A sends money to Account B, and Account B sends a similar amount (within 10%) back to Account A within a 24-hour window.

- **Table Schema**:
```sql
CREATE TABLE transactions (
    transaction_id VARCHAR(20) PRIMARY KEY,
    sender_account_id VARCHAR(20) NOT NULL,
    receiver_account_id VARCHAR(20) NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    transaction_timestamp TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'COMPLETED'
);
```

- **SQL Query**:
```sql
SELECT 
    t1.transaction_id AS leg1_txn_id,
    t1.sender_account_id AS account_a,
    t1.receiver_account_id AS account_b,
    t1.amount AS leg1_amount,
    t1.transaction_timestamp AS leg1_timestamp,
    t2.transaction_id AS leg2_txn_id,
    t2.amount AS leg2_amount,
    t2.transaction_timestamp AS leg2_timestamp,
    ROUND(ABS(t2.amount - t1.amount), 2) AS amount_diff,
    ROUND(ABS(t2.amount - t1.amount) * 100.0 / t1.amount, 2) AS pct_diff,
    ROUND((JULIANDAY(t2.transaction_timestamp) - JULIANDAY(t1.transaction_timestamp)) * 24.0, 2) AS hours_between
FROM transactions t1
INNER JOIN transactions t2
    ON t1.sender_account_id = t2.receiver_account_id
   AND t1.receiver_account_id = t2.sender_account_id
WHERE t2.transaction_timestamp > t1.transaction_timestamp
  AND (JULIANDAY(t2.transaction_timestamp) - JULIANDAY(t1.transaction_timestamp)) * 24.0 <= 24.0
  AND ABS(t2.amount - t1.amount) <= (0.10 * t1.amount)
  AND t1.status = 'COMPLETED'
  AND t2.status = 'COMPLETED'
ORDER BY t1.transaction_timestamp;
```

- **Execution Results**:
| leg1_txn_id | account_a | account_b | leg1_amount | leg1_timestamp | leg2_txn_id | leg2_amount | leg2_timestamp | amount_diff | pct_diff | hours_between |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| **TXN_001** | ACC_101 | ACC_202 | 1000.00 | 2024-05-10 09:00:00 | **TXN_002** | 950.00 | 2024-05-10 13:00:00 | 50.00 | 5.00% | 4.00h |
| **TXN_003** | ACC_303 | ACC_404 | 500.00 | 2024-05-11 08:30:00 | **TXN_004** | 500.00 | 2024-05-12 02:30:00 | 0.00 | 0.00% | 18.00h |
| **TXN_010** | ACC_222 | ACC_333 | 1500.00 | 2024-05-15 10:00:00 | **TXN_011** | 1600.00 | 2024-05-15 16:30:00 | 100.00 | 6.67% | 6.50h |

---

#### Scenario 2: IPL Player Performance Streaks (2024 Season)
**Objective**: Identify players who scored 30+ runs in at least 3 consecutive matches. Return the player's name and the date the scoring streak commenced.

- **Table Schema**:
```sql
CREATE TABLE ipl_match_scores (
    match_id INT,
    match_date DATE NOT NULL,
    player_id VARCHAR(20) NOT NULL,
    player_name VARCHAR(100) NOT NULL,
    team VARCHAR(50),
    opponent VARCHAR(50),
    runs_scored INT NOT NULL,
    balls_faced INT,
    PRIMARY KEY (match_id, player_id)
);
```

- **SQL Query (Island-and-Gaps Pattern via Window Functions)**:
```sql
WITH player_match_sequence AS (
    SELECT 
        match_id,
        match_date,
        player_id,
        player_name,
        runs_scored,
        ROW_NUMBER() OVER (
            PARTITION BY player_id 
            ORDER BY match_date, match_id
        ) AS overall_match_seq
    FROM ipl_match_scores
),
qualifying_matches AS (
    SELECT 
        match_id,
        match_date,
        player_id,
        player_name,
        runs_scored,
        overall_match_seq,
        ROW_NUMBER() OVER (
            PARTITION BY player_id 
            ORDER BY match_date, match_id
        ) AS qualifying_seq,
        (overall_match_seq - ROW_NUMBER() OVER (
            PARTITION BY player_id 
            ORDER BY match_date, match_id
        )) AS streak_group_id
    FROM player_match_sequence
    WHERE runs_scored >= 30
),
streaks_aggregated AS (
    SELECT 
        player_name,
        MIN(match_date) AS streak_commenced_date,
        MAX(match_date) AS streak_concluded_date,
        COUNT(*) AS consecutive_matches,
        GROUP_CONCAT(runs_scored, ', ') AS scores_in_streak
    FROM qualifying_matches
    GROUP BY player_id, player_name, streak_group_id
    HAVING COUNT(*) >= 3
)
SELECT 
    player_name,
    streak_commenced_date,
    consecutive_matches,
    streak_concluded_date,
    scores_in_streak
FROM streaks_aggregated
ORDER BY streak_commenced_date, player_name;
```

- **Execution Results**:
| Player Name | Streak Commenced Date | Consecutive Matches | Streak Concluded Date | Scores in Streak |
|:---|:---|:---|:---|:---|
| **Virat Kohli** | **2024-04-06** | 4 | 2024-04-21 | 113, 42, 42, 51 |
| **KL Rahul** | **2024-04-07** | 3 | 2024-04-19 | 33, 39, 82 |
| **Rohit Sharma** | **2024-04-07** | 3 | 2024-04-14 | 49, 38, 105 |
| **Ruturaj Gaikwad** | **2024-04-08** | 5 | 2024-04-28 | 67, 69, 43, 108, 98 |

---

## 📷 Screenshots & Visual Evidence

- **Web Application Dashboard**: [01_dashboard_initial_load.png](reports/screenshots/01_dashboard_initial_load.png)
- **Visual Chart & Rendering**: [03_chart_visual_rendering.png](reports/screenshots/03_chart_visual_rendering.png)
- **Amortization Report View**: [04_amortization_report_view.png](reports/screenshots/04_amortization_report_view.png)
- **SQL Execution Report**: [sql_all_scenarios_combined.png](reports/screenshots/sql_all_scenarios_combined.png)
- **Scenario 1 Output**: [sql_scenario1_roundtrip_results.png](reports/screenshots/sql_scenario1_roundtrip_results.png)
- **Scenario 2 Output**: [sql_scenario2_ipl_streaks_results.png](reports/screenshots/sql_scenario2_ipl_streaks_results.png)

---
© 2026 Streamhub LTD. Assessment Solution.
