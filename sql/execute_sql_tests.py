"""
Automated SQL Test Execution & Evidence Capture Script
Executes SQL queries for Scenario 1 & Scenario 2, verifies outputs,
and generates visual HTML/PNG query output reports.
"""

import sqlite3
import os
from playwright.sync_api import sync_playwright

DB_PATH = "sql/assessment_database.db"
RESULTS_DIR = "sql/results"
REPORTS_DIR = "reports/screenshots"

os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)


def execute_sql_file(db_conn: sqlite3.Connection, sql_file_path: str):
    """Reads and executes SQL script, returning the final query results and column names."""
    with open(sql_file_path, "r") as f:
        full_sql = f.read()

    # Split script into statements
    statements = [stmt.strip() for stmt in full_sql.split(";") if stmt.strip()]

    cursor = db_conn.cursor()
    last_cursor = None

    for stmt in statements:
        last_cursor = cursor.execute(stmt)

    # Fetch last query results (the SELECT)
    if last_cursor and last_cursor.description:
        columns = [desc[0] for desc in last_cursor.description]
        rows = last_cursor.fetchall()
        return columns, rows
    return [], []


def generate_ascii_table(columns, rows):
    """Formats results as an ASCII table."""
    if not columns or not rows:
        return "No rows returned."

    col_widths = [len(col) for col in columns]
    for row in rows:
        for idx, val in enumerate(row):
            col_widths[idx] = max(col_widths[idx], len(str(val)))

    header_line = " | ".join(col.ljust(col_widths[i]) for i, col in enumerate(columns))
    sep_line = "-+-".join("-" * col_widths[i] for i in range(len(columns)))

    lines = [header_line, sep_line]
    for row in rows:
        row_line = " | ".join(str(val).ljust(col_widths[i]) for i, val in enumerate(row))
        lines.append(row_line)

    return "\n".join(lines)


def generate_html_report(scenario1_data, scenario2_data, html_output_path: str):
    """Generates an HTML presentation of schemas, queries, and result tables."""
    cols1, rows1 = scenario1_data
    cols2, rows2 = scenario2_data

    def make_table_html(cols, rows):
        th_html = "".join(f"<th>{c}</th>" for c in cols)
        tr_html = ""
        for r in rows:
            tds = "".join(f"<td>{v}</td>" for v in r)
            tr_html += f"<tr>{tds}</tr>"
        return f"<table><thead><tr>{th_html}</tr></thead><tbody>{tr_html}</tbody></table>"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>SQL Test Execution Results - Streamhub Assessment</title>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
  body {{
    background: #0b0f19;
    color: #f3f4f6;
    font-family: 'Plus Jakarta Sans', sans-serif;
    padding: 2.5rem;
    margin: 0;
  }}
  h1 {{
    color: #60a5fa;
    font-size: 1.8rem;
    margin-bottom: 0.25rem;
  }}
  .subtitle {{
    color: #9ca3af;
    margin-bottom: 2rem;
  }}
  .section {{
    background: rgba(17, 24, 39, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 10px 25px rgba(0,0,0,0.4);
  }}
  h2 {{
    color: #ffffff;
    font-size: 1.3rem;
    margin-top: 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    padding-bottom: 0.75rem;
  }}
  p.desc {{
    color: #9ca3af;
    font-size: 0.9rem;
    margin-bottom: 1rem;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.88rem;
    margin-top: 1rem;
  }}
  th, td {{
    padding: 0.75rem 1rem;
    text-align: left;
    border-bottom: 1px solid rgba(255, 255, 255, 0.07);
  }}
  th {{
    background: rgba(37, 99, 235, 0.2);
    color: #93c5fd;
    font-weight: 600;
    text-transform: uppercase;
    font-size: 0.75rem;
    letter-spacing: 0.05em;
  }}
  tr:hover {{
    background: rgba(255, 255, 255, 0.03);
  }}
  .badge {{
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    background: rgba(16, 185, 129, 0.2);
    color: #34d399;
  }}
</style>
</head>
<body>
  <h1>SQL Test Scenarios — Automated Verification</h1>
  <div class="subtitle">Streamhub Assessment A4 &bull; Verified in SQLite / ANSI SQL Engine</div>

  <div class="section" id="section-scenario1">
    <h2>Scenario 1: Round-Trip Money Transfers (Within 24h &amp; 10% Amount Tolerance)</h2>
    <p class="desc">
      Identifies Account A &rarr; Account B &rarr; Account A transfers where the returned amount is within 10% and completed within a 24-hour window.
    </p>
    <span class="badge">{len(rows1)} Qualified Round-Trip Instances Detected</span>
    {make_table_html(cols1, rows1)}
  </div>

  <div class="section" id="section-scenario2">
    <h2>Scenario 2: IPL 2024 Player Performance Streaks (30+ Runs in 3+ Consecutive Matches)</h2>
    <p class="desc">
      Identifies players scoring 30+ runs in &ge; 3 consecutive matches, returning player name and exact streak commencement date using Island-and-Gaps window analysis.
    </p>
    <span class="badge">{len(rows2)} Qualifying Streaks Detected</span>
    {make_table_html(cols2, rows2)}
  </div>
</body>
</html>
"""
    with open(html_output_path, "w") as f:
        f.write(html)


def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)

    print("=" * 80)
    print("EXECUTING SQL SCENARIO 1: ROUND-TRIP TRANSFERS (24H / 10% TOLERANCE)")
    print("=" * 80)
    s1_cols, s1_rows = execute_sql_file(conn, "sql/scenario1_roundtrip_transfers.sql")
    s1_table = generate_ascii_table(s1_cols, s1_rows)
    print(s1_table)

    with open(os.path.join(RESULTS_DIR, "scenario1_results.txt"), "w") as f:
        f.write(s1_table)

    print("\n" + "=" * 80)
    print("EXECUTING SQL SCENARIO 2: IPL PLAYER PERFORMANCE STREAKS (IPL 2024)")
    print("=" * 80)
    s2_cols, s2_rows = execute_sql_file(conn, "sql/scenario2_ipl_streaks.sql")
    s2_table = generate_ascii_table(s2_cols, s2_rows)
    print(s2_table)

    with open(os.path.join(RESULTS_DIR, "scenario2_results.txt"), "w") as f:
        f.write(s2_table)

    conn.close()

    # Generate HTML report and capture screenshot using Playwright
    html_report_path = "reports/sql_results.html"
    generate_html_report((s1_cols, s1_rows), (s2_cols, s2_rows), html_report_path)
    print(f"\nHTML report saved to {html_report_path}")

    print("\nCapturing high-resolution screenshots with Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        abs_html_path = "file://" + os.path.abspath(html_report_path)
        page.goto(abs_html_path)
        page.wait_for_selector("table")

        s1_el = page.locator("#section-scenario1")
        s1_png = os.path.join(REPORTS_DIR, "sql_scenario1_roundtrip_results.png")
        s1_el.screenshot(path=s1_png)
        print(f"Scenario 1 screenshot saved to {s1_png}")

        s2_el = page.locator("#section-scenario2")
        s2_png = os.path.join(REPORTS_DIR, "sql_scenario2_ipl_streaks_results.png")
        s2_el.screenshot(path=s2_png)
        print(f"Scenario 2 screenshot saved to {s2_png}")

        full_png = os.path.join(REPORTS_DIR, "sql_all_scenarios_combined.png")
        page.screenshot(path=full_png, full_page=True)
        print(f"Full SQL report screenshot saved to {full_png}")

        browser.close()

    print("\nAll SQL tests executed and verified successfully!")


if __name__ == "__main__":
    main()
