"""
Dynamic Locator Factory
Provides dynamic, parameterized locators for StreamEMI test automation,
ensuring resilient, maintainable, and decoupled UI element resolution.
"""

from playwright.sync_api import Page, Locator


class DynamicLocators:
    """Dynamic locator generators for StreamEMI elements."""

    @staticmethod
    def metric_card(page: Page, metric_key: str) -> Locator:
        """Dynamically locates summary metric card by metric key (e.g. 'principal', 'interest', 'total')."""
        return page.locator(f'[data-testid="card-{metric_key}"]')

    @staticmethod
    def metric_value(page: Page, metric_name: str) -> Locator:
        """Dynamically locates metric value element (e.g., 'monthly-emi-value', 'total-interest-value')."""
        return page.locator(f'[data-testid="{metric_name}"]')

    @staticmethod
    def numeric_input(page: Page, field_name: str) -> Locator:
        """Dynamically locates numeric inputs by field name ('principal', 'rate', 'tenure')."""
        return page.locator(f'[data-testid="{field_name}-input"]')

    @staticmethod
    def range_slider(page: Page, field_name: str) -> Locator:
        """Dynamically locates range sliders by field name ('principal', 'rate', 'tenure')."""
        return page.locator(f'[data-testid="{field_name}-slider"]')

    @staticmethod
    def unit_toggle(page: Page, unit: str) -> Locator:
        """Dynamically locates tenure unit toggle button ('years' | 'months')."""
        return page.locator(f'[data-testid="unit-{unit}"]')

    @staticmethod
    def view_mode_toggle(page: Page, mode: str) -> Locator:
        """Dynamically locates schedule view toggle button ('yearly' | 'monthly')."""
        return page.locator(f'[data-testid="view-{mode}-btn"]')

    @staticmethod
    def schedule_row(page: Page, period: int) -> Locator:
        """Dynamically locates amortization table row by period number."""
        return page.locator(f'[data-testid="schedule-row"][data-period="{period}"]')

    @staticmethod
    def schedule_cell(page: Page, period: int, cell_class: str) -> Locator:
        """Dynamically locates specific cell in a given period row."""
        return page.locator(f'[data-testid="schedule-row"][data-period="{period}"] td.{cell_class}')
