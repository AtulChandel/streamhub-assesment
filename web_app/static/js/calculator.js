/**
 * StreamEMI - Financial Loan Analytics & Visualization Engine
 * Interactive client-side engine with dual-sync controls, dynamic charts,
 * backend API integration, and amortization schedule reports.
 */

(function () {
  'use strict';

  // DOM Elements
  const principalInput = document.getElementById('principal-input');
  const principalSlider = document.getElementById('principal-slider');
  const rateInput = document.getElementById('rate-input');
  const rateSlider = document.getElementById('rate-slider');
  const tenureInput = document.getElementById('tenure-input');
  const tenureSlider = document.getElementById('tenure-slider');

  const unitYearsBtn = document.getElementById('unit-years');
  const unitMonthsBtn = document.getElementById('unit-months');
  const calculateBtn = document.getElementById('calculate-btn');
  const resetBtn = document.getElementById('reset-btn');
  const currencySelect = document.getElementById('currency-select');
  const currencySymbols = document.querySelectorAll('.curr-symbol');

  // Summary Elements
  const monthlyEmiValue = document.getElementById('monthly-emi-value');
  const totalInterestValue = document.getElementById('total-interest-value');
  const totalPaymentValue = document.getElementById('total-payment-value');
  const summaryPrincipalValue = document.getElementById('summary-principal-value');
  const summaryTenureBadge = document.getElementById('summary-tenure-badge');

  // Chart Elements
  const donutPrincipalSlice = document.getElementById('donut-slice-principal');
  const donutInterestSlice = document.getElementById('donut-slice-interest');
  const donutCenterAmount = document.getElementById('donut-center-amount');
  const legendPrincipalPct = document.getElementById('legend-principal-pct');
  const legendInterestPct = document.getElementById('legend-interest-pct');

  // Report Elements
  const viewYearlyBtn = document.getElementById('view-yearly-btn');
  const viewMonthlyBtn = document.getElementById('view-monthly-btn');
  const scheduleFilterInput = document.getElementById('schedule-filter-input');
  const exportCsvBtn = document.getElementById('export-csv-btn');
  const scheduleTbody = document.getElementById('schedule-tbody');
  const thPeriod = document.getElementById('th-period');
  const backendStatusBadge = document.getElementById('backend-status-badge');

  // Application State
  let currentCurrency = '$';
  let tenureUnit = 'years'; // 'years' | 'months'
  let reportMode = 'yearly'; // 'yearly' | 'monthly'
  let scheduleData = { yearly: [], monthly: [] };

  const CIRCLE_CIRCUMFERENCE = 2 * Math.PI * 70; // r=70 -> ~439.82

  /**
   * Currency & Number Formatting Helpers
   */
  function formatCurrency(amount) {
    if (isNaN(amount) || amount === null) return `${currentCurrency}0.00`;
    const formatted = Number(amount).toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
    return `${currentCurrency}${formatted}`;
  }

  function formatCompactNumber(amount) {
    if (isNaN(amount) || amount === null) return '0';
    if (amount >= 10000000) return `${currentCurrency}${(amount / 10000000).toFixed(2)}Cr`;
    if (amount >= 1000000) return `${currentCurrency}${(amount / 1000000).toFixed(2)}M`;
    if (amount >= 1000) return `${currentCurrency}${(amount / 1000).toFixed(1)}K`;
    return `${currentCurrency}${amount.toFixed(0)}`;
  }

  /**
   * Core Mathematical EMI Calculation (Independently computed client-side)
   * Formula: E = P * r * (1 + r)^n / ((1 + r)^n - 1)
   */
  function calculateEmi(principal, annualRate, tenureMonths) {
    if (principal <= 0 || tenureMonths <= 0) {
      return {
        monthlyEmi: 0,
        totalInterest: 0,
        totalPayment: 0,
        principalPct: 100,
        interestPct: 0,
      };
    }

    const monthlyRate = (annualRate / 100) / 12;

    if (monthlyRate === 0) {
      const emi = principal / tenureMonths;
      return {
        monthlyEmi: emi,
        totalInterest: 0,
        totalPayment: principal,
        principalPct: 100,
        interestPct: 0,
      };
    }

    const compounded = Math.pow(1 + monthlyRate, tenureMonths);
    const monthlyEmi = (principal * monthlyRate * compounded) / (compounded - 1);
    const totalPayment = monthlyEmi * tenureMonths;
    const totalInterest = totalPayment - principal;

    const principalPct = (principal / totalPayment) * 100;
    const interestPct = (totalInterest / totalPayment) * 100;

    return {
      monthlyEmi: Math.round(monthlyEmi * 100) / 100,
      totalInterest: Math.round(totalInterest * 100) / 100,
      totalPayment: Math.round(totalPayment * 100) / 100,
      principalPct: Math.round(principalPct * 10) / 10,
      interestPct: Math.round(interestPct * 10) / 10,
    };
  }

  /**
   * Generate Full Amortization Schedule
   */
  function buildAmortizationSchedule(principal, annualRate, tenureMonths) {
    const monthlyRate = (annualRate / 100) / 12;
    const base = calculateEmi(principal, annualRate, tenureMonths);
    const monthlyEmi = base.monthlyEmi;

    let balance = principal;
    const monthlyList = [];
    const yearlyMap = {};

    for (let m = 1; m <= tenureMonths; m++) {
      const interestPaid = balance * monthlyRate;
      let principalPaid = monthlyEmi - interestPaid;
      let actualEmi = monthlyEmi;

      if (balance < principalPaid || m === tenureMonths) {
        principalPaid = balance;
        actualEmi = principalPaid + interestPaid;
        balance = 0;
      } else {
        balance -= principalPaid;
      }

      const openingBalance = balance + principalPaid;
      const repaidPct = Math.round(((principal - balance) / principal) * 1000) / 10;
      const yearNum = Math.floor((m - 1) / 12) + 1;

      const monthItem = {
        period: m,
        year: yearNum,
        openingBalance: Math.round(openingBalance * 100) / 100,
        emi: Math.round(actualEmi * 100) / 100,
        principalPaid: Math.round(principalPaid * 100) / 100,
        interestPaid: Math.round(interestPaid * 100) / 100,
        closingBalance: Math.round(Math.max(0, balance) * 100) / 100,
        paidPct: repaidPct,
      };
      monthlyList.push(monthItem);

      if (!yearlyMap[yearNum]) {
        yearlyMap[yearNum] = {
          period: yearNum,
          year: yearNum,
          openingBalance: Math.round(openingBalance * 100) / 100,
          emi: 0,
          principalPaid: 0,
          interestPaid: 0,
          closingBalance: 0,
          paidPct: 0,
        };
      }

      yearlyMap[yearNum].emi += actualEmi;
      yearlyMap[yearNum].principalPaid += principalPaid;
      yearlyMap[yearNum].interestPaid += interestPaid;
      yearlyMap[yearNum].closingBalance = Math.round(Math.max(0, balance) * 100) / 100;
      yearlyMap[yearNum].paidPct = repaidPct;
    }

    const yearlyList = Object.keys(yearlyMap).map(y => {
      const item = yearlyMap[y];
      return {
        period: Number(y),
        year: Number(y),
        openingBalance: item.openingBalance,
        emi: Math.round(item.emi * 100) / 100,
        principalPaid: Math.round(item.principalPaid * 100) / 100,
        interestPaid: Math.round(item.interestPaid * 100) / 100,
        closingBalance: item.closingBalance,
        paidPct: item.paidPct,
      };
    });

    return { yearly: yearlyList, monthly: monthlyList };
  }

  /**
   * Update Donut Chart Rendering (Visual Element)
   */
  function updateVisualDonutChart(principal, totalInterest, totalPayment, principalPct, interestPct) {
    if (totalPayment <= 0) return;

    // Circumference fraction
    const pDash = (principalPct / 100) * CIRCLE_CIRCUMFERENCE;
    const iDash = (interestPct / 100) * CIRCLE_CIRCUMFERENCE;

    donutPrincipalSlice.setAttribute('stroke-dasharray', `${pDash.toFixed(2)} ${CIRCLE_CIRCUMFERENCE.toFixed(2)}`);
    donutPrincipalSlice.setAttribute('stroke-dashoffset', '0');

    donutInterestSlice.setAttribute('stroke-dasharray', `${iDash.toFixed(2)} ${CIRCLE_CIRCUMFERENCE.toFixed(2)}`);
    donutInterestSlice.setAttribute('stroke-dashoffset', `-${pDash.toFixed(2)}`);

    donutCenterAmount.textContent = formatCompactNumber(totalPayment);
    legendPrincipalPct.textContent = `${principalPct.toFixed(1)}%`;
    legendInterestPct.textContent = `${interestPct.toFixed(1)}%`;
  }

  /**
   * Render Amortization Schedule Table (Report Element)
   */
  function renderScheduleTable() {
    const list = reportMode === 'yearly' ? scheduleData.yearly : scheduleData.monthly;
    thPeriod.textContent = reportMode === 'yearly' ? 'Year' : 'Month';

    const filterTerm = (scheduleFilterInput.value || '').trim().toLowerCase();

    let filtered = list;
    if (filterTerm) {
      filtered = list.filter(row => {
        const pStr = String(row.period);
        const yStr = String(row.year);
        return pStr.includes(filterTerm) || yStr.includes(filterTerm);
      });
    }

    scheduleTbody.innerHTML = '';

    if (filtered.length === 0) {
      const emptyRow = document.createElement('tr');
      emptyRow.innerHTML = `<td colspan="7" style="text-align: center; color: var(--text-dim); padding: 2rem;">No matching amortization records found</td>`;
      scheduleTbody.appendChild(emptyRow);
      return;
    }

    const fragment = document.createDocumentFragment();
    filtered.forEach(row => {
      const tr = document.createElement('tr');
      tr.setAttribute('data-testid', 'schedule-row');
      tr.setAttribute('data-period', row.period);
      tr.setAttribute('data-year', row.year);

      tr.innerHTML = `
        <td style="font-weight: 700;">${reportMode === 'yearly' ? 'Year ' + row.period : 'Month ' + row.period}</td>
        <td>${formatCurrency(row.openingBalance)}</td>
        <td style="font-weight: 600;">${formatCurrency(row.emi)}</td>
        <td class="principal-cell">${formatCurrency(row.principalPaid)}</td>
        <td class="interest-cell">${formatCurrency(row.interestPaid)}</td>
        <td>${formatCurrency(row.closingBalance)}</td>
        <td class="progress-cell">${row.paidPct.toFixed(1)}%</td>
      `;
      fragment.appendChild(tr);
    });

    scheduleTbody.appendChild(fragment);
  }

  /**
   * Main Recalculate & Render Trigger
   */
  function recalculateAll() {
    const principal = parseFloat(principalInput.value) || 0;
    const rate = parseFloat(rateInput.value) || 0;
    const tenureVal = parseFloat(tenureInput.value) || 0;
    const tenureMonths = tenureUnit === 'years' ? Math.round(tenureVal * 12) : Math.round(tenureVal);

    // Compute EMI values
    const result = calculateEmi(principal, rate, tenureMonths);

    // Update UI Summary Elements
    monthlyEmiValue.textContent = formatCurrency(result.monthlyEmi);
    totalInterestValue.textContent = formatCurrency(result.totalInterest);
    totalPaymentValue.textContent = formatCurrency(result.totalPayment);
    summaryPrincipalValue.textContent = formatCurrency(principal);

    const tenureLabel = tenureUnit === 'years' 
      ? `${tenureVal} Year${tenureVal === 1 ? '' : 's'}` 
      : `${tenureVal} Month${tenureVal === 1 ? '' : 's'}`;
    summaryTenureBadge.textContent = `Based on ${tenureLabel} Tenure (${tenureMonths} Mo)`;

    // Update Visual Chart
    updateVisualDonutChart(principal, result.totalInterest, result.totalPayment, result.principalPct, result.interestPct);

    // Build Amortization Schedules
    scheduleData = buildAmortizationSchedule(principal, rate, tenureMonths);
    renderScheduleTable();
  }

  /**
   * Sync Input and Slider Helpers
   */
  function syncNumericAndSlider(inputEl, sliderEl) {
    inputEl.addEventListener('input', () => {
      sliderEl.value = inputEl.value;
      recalculateAll();
    });
    sliderEl.addEventListener('input', () => {
      inputEl.value = sliderEl.value;
      recalculateAll();
    });
  }

  /**
   * Export Amortization Table to CSV
   */
  function exportToCsv() {
    const list = reportMode === 'yearly' ? scheduleData.yearly : scheduleData.monthly;
    if (!list || list.length === 0) return;

    const headers = ['Period', 'Year', 'Opening_Balance', 'EMI_Paid', 'Principal_Paid', 'Interest_Paid', 'Closing_Balance', 'Loan_Repaid_Pct'];
    const rows = list.map(r => [
      r.period,
      r.year,
      r.openingBalance,
      r.emi,
      r.principalPaid,
      r.interestPaid,
      r.closingBalance,
      r.paidPct + '%',
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' +
      [headers.join(','), ...rows.map(e => e.join(','))].join('\n');

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `StreamEMI_Schedule_${reportMode}_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  /**
   * Check Backend Health
   */
  async function checkBackendHealth() {
    try {
      const res = await fetch('/api/health');
      if (res.ok) {
        backendStatusBadge.style.display = 'flex';
      }
    } catch (e) {
      // Backend not running or static mode
      backendStatusBadge.innerHTML = '<span class="status-text" style="color: #9ca3af;">Client Engine Active</span>';
    }
  }

  /**
   * Event Listeners Setup
   */
  function setupEventListeners() {
    // Dual Sync Controls
    syncNumericAndSlider(principalInput, principalSlider);
    syncNumericAndSlider(rateInput, rateSlider);
    syncNumericAndSlider(tenureInput, tenureSlider);

    // Tenure Unit Toggle
    unitYearsBtn.addEventListener('click', () => {
      if (tenureUnit === 'years') return;
      tenureUnit = 'years';
      unitYearsBtn.classList.add('active');
      unitMonthsBtn.classList.remove('active');

      // Convert months to years
      const currVal = parseFloat(tenureInput.value) || 240;
      const years = Math.max(1, Math.min(40, Math.round(currVal / 12)));
      tenureInput.max = '40';
      tenureInput.value = years;
      tenureSlider.max = '35';
      tenureSlider.value = years;

      document.getElementById('tenure-min-label').textContent = '1 Yr';
      document.getElementById('tenure-mid-label').textContent = '18 Yr';
      document.getElementById('tenure-max-label').textContent = '35 Yr';

      recalculateAll();
    });

    unitMonthsBtn.addEventListener('click', () => {
      if (tenureUnit === 'months') return;
      tenureUnit = 'months';
      unitMonthsBtn.classList.add('active');
      unitYearsBtn.classList.remove('active');

      // Convert years to months
      const currVal = parseFloat(tenureInput.value) || 20;
      const months = Math.min(480, Math.round(currVal * 12));
      tenureInput.max = '480';
      tenureInput.value = months;
      tenureSlider.max = '420';
      tenureSlider.value = months;

      document.getElementById('tenure-min-label').textContent = '12 Mo';
      document.getElementById('tenure-mid-label').textContent = '210 Mo';
      document.getElementById('tenure-max-label').textContent = '420 Mo';

      recalculateAll();
    });

    // Calculate Button Trigger
    calculateBtn.addEventListener('click', recalculateAll);

    // Reset Button
    resetBtn.addEventListener('click', () => {
      principalInput.value = '1000000';
      principalSlider.value = '1000000';
      rateInput.value = '8.5';
      rateSlider.value = '8.5';

      tenureUnit = 'years';
      unitYearsBtn.classList.add('active');
      unitMonthsBtn.classList.remove('active');
      tenureInput.max = '40';
      tenureInput.value = '20';
      tenureSlider.max = '35';
      tenureSlider.value = '20';

      scheduleFilterInput.value = '';
      reportMode = 'yearly';
      viewYearlyBtn.classList.add('active');
      viewMonthlyBtn.classList.remove('active');

      recalculateAll();
    });

    // Currency Selector
    currencySelect.addEventListener('change', (e) => {
      currentCurrency = e.target.value;
      currencySymbols.forEach(el => el.textContent = currentCurrency);
      recalculateAll();
    });

    // View Mode Toggle
    viewYearlyBtn.addEventListener('click', () => {
      reportMode = 'yearly';
      viewYearlyBtn.classList.add('active');
      viewMonthlyBtn.classList.remove('active');
      renderScheduleTable();
    });

    viewMonthlyBtn.addEventListener('click', () => {
      reportMode = 'monthly';
      viewMonthlyBtn.classList.add('active');
      viewYearlyBtn.classList.remove('active');
      renderScheduleTable();
    });

    // Filter Input
    scheduleFilterInput.addEventListener('input', renderScheduleTable);

    // Export CSV
    exportCsvBtn.addEventListener('click', exportToCsv);
  }

  // Initialize
  document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    recalculateAll();
    checkBackendHealth();
  });

})();
