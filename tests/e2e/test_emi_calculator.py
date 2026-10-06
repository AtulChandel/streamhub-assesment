"""
Playwright End-to-End Test Suite: StreamEMI Calculator
Covers:
1. Dashboard navigation, layout, and visual component loading.
2. Independent mathematical verification of calculated outputs (EMI, Interest, Total).
3. Visual element rendering, visibility, and non-zero chart slice data verification.
4. User input mutation, tenure toggling, dynamic currency switching, and amortization reporting.
"""

import pytest
from playwright.sync_api import Page, expect
from tests.config.environment import get_current_environment
from tests.e2e.pages.emi_calculator_page import EmiCalculatorPage
from tests.utils.emi_math import compute_expected_emi, is_approximately_equal


@pytest.fixture(scope="function")
def emi_page(page: Page) -> EmiCalculatorPage:
    env = get_current_environment()
    emi_p = EmiCalculatorPage(page, env.base_url)
    emi_p.navigate()
    return emi_p


class TestEmiDashboardNavigation:
    """Test Suite 1: Dashboard navigation, layout, and view integrity."""

    def test_dashboard_loads_successfully(self, emi_page: EmiCalculatorPage):
        """Validates that navigation to dashboard succeeds and core views load correctly."""
        # 1. Page Title Check
        title = emi_page.get_title()
        assert "StreamEMI" in title, f"Unexpected page title: {title}"

        # 2. Main Brand Heading
        heading = emi_page.get_heading()
        assert "StreamEMI" in heading, f"Unexpected heading text: {heading}"

        # 3. Input Controls Card is visible
        expect(emi_page.page.locator('[data-testid="input-controls-card"]')).to_be_visible()

        # 4. Summary Dashboard Card is visible
        expect(emi_page.page.locator('[data-testid="summary-dashboard-card"]')).to_be_visible()

        # 5. Visual Chart Container is visible
        expect(emi_page.chart_container).to_be_visible()

        # 6. Report Section & Amortization Table are visible
        expect(emi_page.schedule_table).to_be_visible()

        # Capture audit screenshot
        screenshot_path = emi_page.capture_screenshot("01_dashboard_initial_load")
        assert screenshot_path is not None


class TestEmiMathematicalCalculation:
    """Test Suite 2: Validates calculated outputs against independently computed mathematical expected values."""

    def test_default_values_match_independent_computation(self, emi_page: EmiCalculatorPage):
        """
        Validates default loan:
          Principal: $1,000,000
          Rate: 8.5%
          Tenure: 20 Years (240 months)
        """
        principal = 1000000.0
        annual_rate = 8.5
        tenure_months = 20 * 12

        # Independently computed expected values
        expected = compute_expected_emi(principal, annual_rate, tenure_months)

        # UI displayed values
        ui_emi = emi_page.get_monthly_emi()
        ui_interest = emi_page.get_total_interest()
        ui_total = emi_page.get_total_payment()
        ui_principal = emi_page.get_principal_summary()

        # Assertions with strict tolerance ($1.00 for rounding)
        assert is_approximately_equal(ui_principal, principal), f"Principal mismatch: {ui_principal} vs {principal}"
        assert is_approximately_equal(ui_emi, expected["monthly_emi"]), f"EMI mismatch: UI={ui_emi}, Exp={expected['monthly_emi']}"
        assert is_approximately_equal(ui_interest, expected["total_interest"]), f"Interest mismatch: UI={ui_interest}, Exp={expected['total_interest']}"
        assert is_approximately_equal(ui_total, expected["total_payment"]), f"Total mismatch: UI={ui_total}, Exp={expected['total_payment']}"

    @pytest.mark.parametrize(
        "principal, rate, tenure, unit",
        [
            (50000.0, 7.5, 5, "years"),      # Scenario A: Auto / Personal Loan
            (500000.0, 6.8, 15, "years"),    # Scenario B: Mid-term Home Loan
            (1200000.0, 9.2, 25, "years"),   # Scenario C: Long-term Commercial Mortgage
            (80000.0, 11.5, 36, "months"),   # Scenario D: Short-term Loan in Months
        ],
    )
    def test_user_input_submission_and_dynamic_calculation(
        self, emi_page: EmiCalculatorPage, principal: float, rate: float, tenure: int, unit: str
    ):
        """
        Submits varied user inputs across loan amounts, interest rates, and tenures,
        and verifies calculated/displayed output matches independently computed expected values.
        """
        # Set inputs
        emi_page.set_principal(principal)
        emi_page.set_interest_rate(rate)
        emi_page.set_tenure(tenure, unit)
        emi_page.click_calculate()

        # Compute independent expected values
        tenure_months = tenure * 12 if unit == "years" else tenure
        expected = compute_expected_emi(principal, rate, tenure_months)

        # Retrieve UI outputs
        ui_emi = emi_page.get_monthly_emi()
        ui_interest = emi_page.get_total_interest()
        ui_total = emi_page.get_total_payment()

        # Assert independent match
        assert is_approximately_equal(ui_emi, expected["monthly_emi"], tolerance=1.5), (
            f"EMI calculation failed for P={principal}, R={rate}, T={tenure} {unit}: "
            f"UI={ui_emi}, Expected={expected['monthly_emi']}"
        )
        assert is_approximately_equal(ui_interest, expected["total_interest"], tolerance=5.0), (
            f"Total Interest mismatch: UI={ui_interest}, Expected={expected['total_interest']}"
        )
        assert is_approximately_equal(ui_total, expected["total_payment"], tolerance=5.0), (
            f"Total Payment mismatch: UI={ui_total}, Expected={expected['total_payment']}"
        )

        emi_page.capture_screenshot(f"02_calc_{int(principal)}_{unit}_{tenure}")


class TestVisualElementAndChart:
    """Test Suite 3: Chart / visual element visibility and non-zero valid data rendering."""

    def test_visual_chart_renders_non_zero_valid_data(self, emi_page: EmiCalculatorPage):
        """Verifies visibility of the Donut visual chart and confirms non-zero valid data rendering."""
        # 1. Visual chart element is visible
        assert emi_page.is_chart_visible() is True, "Donut chart SVG is not visible in the DOM"

        # 2. Extract slice stroke data
        dash_data = emi_page.get_chart_stroke_data()
        p_dash = dash_data["principal_dash"]
        i_dash = dash_data["interest_dash"]

        # Parse principal dash value (e.g. '211.11 439.82')
        p_val = float(p_dash.split()[0]) if p_dash else 0.0
        i_val = float(i_dash.split()[0]) if i_dash else 0.0

        assert p_val > 0.0, f"Principal donut slice rendered with zero/empty stroke: {p_dash}"
        assert i_val > 0.0, f"Interest donut slice rendered with zero/empty stroke: {i_dash}"

        # 3. Sum of arcs should equal full circumference (~439.82)
        total_dash = p_val + i_val
        assert 435.0 <= total_dash <= 445.0, f"Donut slices sum ({total_dash}) did not match expected circumference"

        # 4. Center label is non-empty
        center_text = emi_page.page.locator("#donut-center-amount").text_content() or ""
        assert len(center_text.strip()) > 1, f"Donut center total was empty: '{center_text}'"

        emi_page.capture_screenshot("03_chart_visual_rendering")


class TestAmortizationReportView:
    """Test Suite 4: Report / detail view driven by user input, filtering, and table validation."""

    def test_amortization_schedule_table_rows_and_filtering(self, emi_page: EmiCalculatorPage):
        """Validates amortization report table loads rows, displays breakdown, and responds to filter."""
        # By default for 20 years, yearly view should have 20 rows
        row_count = emi_page.get_schedule_row_count()
        assert row_count == 20, f"Expected 20 yearly rows for 20 years tenure, got {row_count}"

        # First row should be Year 1
        assert emi_page.get_schedule_row_period(0) == 1

        # Last row should be Year 20 with 100% repaid
        last_row = emi_page.page.locator('[data-testid="schedule-row"]').nth(19)
        last_repaid_text = last_row.locator("td.progress-cell").inner_text()
        assert "100" in last_repaid_text, f"Expected final row to show 100% repaid, got {last_repaid_text}"

        # Test filtering: filter for "Year 5"
        emi_page.filter_schedule("5")
        filtered_count = emi_page.get_schedule_row_count()
        # Should match rows containing 5 (e.g., Year 5, Year 15)
        assert 1 <= filtered_count <= 5, f"Unexpected filtered count: {filtered_count}"

        # Clear filter
        emi_page.filter_schedule("")
        assert emi_page.get_schedule_row_count() == 20

        # Switch to Monthly View
        emi_page.switch_schedule_mode("monthly")
        monthly_count = emi_page.get_schedule_row_count()
        assert monthly_count == 240, f"Expected 240 monthly rows, got {monthly_count}"

        emi_page.capture_screenshot("04_amortization_report_view")
