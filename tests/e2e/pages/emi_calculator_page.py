"""
Page Object Model (POM): StreamEMI Calculator Page
Encapsulates all locators, user interactions, and visual verifications for the EMI Dashboard.
"""

from playwright.sync_api import Page, expect
from tests.utils.dynamic_locators import DynamicLocators
from tests.utils.emi_math import parse_currency
import os


class EmiCalculatorPage:
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url

        # Static locators
        self.app_heading = page.locator("#app-heading")
        self.calculate_button = page.locator('[data-testid="calculate-btn"]')
        self.reset_button = page.locator('[data-testid="reset-btn"]')
        self.currency_select = page.locator('[data-testid="currency-select"]')
        self.chart_container = page.locator('[data-testid="chart-container"]')
        self.donut_chart_svg = page.locator('[data-testid="emi-donut-chart"]')
        self.donut_principal_slice = page.locator('[data-testid="donut-slice-principal"]')
        self.donut_interest_slice = page.locator('[data-testid="donut-slice-interest"]')
        self.schedule_table = page.locator('[data-testid="amortization-table"]')
        self.schedule_tbody = page.locator('[data-testid="schedule-tbody"]')
        self.schedule_filter_input = page.locator('[data-testid="schedule-filter-input"]')
        self.export_csv_button = page.locator('[data-testid="export-csv-btn"]')

    def navigate(self):
        """Navigates to the StreamEMI web application."""
        self.page.goto(self.base_url, wait_until="networkidle")
        self.page.wait_for_selector("#app", state="visible")
        return self

    def get_title(self) -> str:
        """Returns the page title."""
        return self.page.title()

    def get_heading(self) -> str:
        """Returns main heading text."""
        return self.app_heading.inner_text().strip()

    # Dynamic Field Setters
    def set_principal(self, amount: float):
        """Sets the principal loan amount input."""
        input_loc = DynamicLocators.numeric_input(self.page, "principal")
        input_loc.click()
        input_loc.fill(str(int(amount) if int(amount) == amount else amount))
        # Trigger change / input event
        input_loc.press("Tab")
        return self

    def set_interest_rate(self, rate: float):
        """Sets the annual interest rate input."""
        input_loc = DynamicLocators.numeric_input(self.page, "rate")
        input_loc.click()
        input_loc.fill(str(rate))
        input_loc.press("Tab")
        return self

    def set_tenure(self, value: int, unit: str = "years"):
        """Sets the tenure and toggles between years or months."""
        unit_loc = DynamicLocators.unit_toggle(self.page, unit)
        unit_loc.click()

        input_loc = DynamicLocators.numeric_input(self.page, "tenure")
        input_loc.click()
        input_loc.fill(str(value))
        input_loc.press("Tab")
        return self

    def click_calculate(self):
        """Clicks the Calculate EMI button."""
        self.calculate_button.click()
        self.page.wait_for_timeout(200)
        return self

    def click_reset(self):
        """Clicks the Reset Defaults button."""
        self.reset_button.click()
        self.page.wait_for_timeout(200)
        return self

    def select_currency(self, symbol: str):
        """Selects currency ($ / ₹ / € / £)."""
        self.currency_select.select_option(symbol)
        self.page.wait_for_timeout(200)
        return self

    # Dynamic Metric Getters
    def get_monthly_emi(self) -> float:
        """Reads and parses Monthly EMI value."""
        text = DynamicLocators.metric_value(self.page, "monthly-emi-value").inner_text()
        return parse_currency(text)

    def get_total_interest(self) -> float:
        """Reads and parses Total Interest value."""
        text = DynamicLocators.metric_value(self.page, "total-interest-value").inner_text()
        return parse_currency(text)

    def get_total_payment(self) -> float:
        """Reads and parses Total Payment value."""
        text = DynamicLocators.metric_value(self.page, "total-payment-value").inner_text()
        return parse_currency(text)

    def get_principal_summary(self) -> float:
        """Reads and parses Summary Principal value."""
        text = DynamicLocators.metric_value(self.page, "summary-principal-value").inner_text()
        return parse_currency(text)

    # Visual Chart Verifications
    def is_chart_visible(self) -> bool:
        """Checks if visual SVG chart is visible."""
        return self.donut_chart_svg.is_visible()

    def get_chart_stroke_data(self) -> dict:
        """Extracts stroke dash values to ensure non-zero visual data rendering."""
        p_dash = self.donut_principal_slice.get_attribute("stroke-dasharray") or ""
        i_dash = self.donut_interest_slice.get_attribute("stroke-dasharray") or ""
        return {
            "principal_dash": p_dash,
            "interest_dash": i_dash,
        }

    # Amortization Report Verifications
    def switch_schedule_mode(self, mode: str):
        """Switches schedule view mode ('yearly' or 'monthly')."""
        DynamicLocators.view_mode_toggle(self.page, mode).click()
        self.page.wait_for_timeout(200)
        return self

    def filter_schedule(self, term: str):
        """Enters search term into the schedule filter input."""
        self.schedule_filter_input.fill(term)
        self.page.wait_for_timeout(200)
        return self

    def get_schedule_row_count(self) -> int:
        """Returns the number of visible schedule rows."""
        return self.page.locator('[data-testid="schedule-row"]').count()

    def get_schedule_row_period(self, index: int) -> int:
        """Returns the period of the row at index."""
        row = self.page.locator('[data-testid="schedule-row"]').nth(index)
        return int(row.get_attribute("data-period") or "0")

    def capture_screenshot(self, name: str, output_dir: str = "reports/screenshots"):
        """Saves a screenshot for test audit reporting."""
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, f"{name}.png")
        self.page.screenshot(path=path, full_page=True)
        return path
