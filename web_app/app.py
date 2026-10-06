"""
StreamEMI Financial Analytics Web Application
A modern, responsive loan & mortgage EMI calculator with real-time analytics,
interactive visual charts, and detailed amortization reports.
"""

from flask import Flask, render_template, request, jsonify
import math

app = Flask(__name__)


def calculate_emi_data(principal: float, annual_rate: float, tenure_months: int):
    """
    Computes standard Equated Monthly Installment (EMI) and breakdown.
    Formula:
      E = P * r * (1 + r)^n / ((1 + r)^n - 1)
      where:
        P = Principal loan amount
        r = Monthly interest rate (annual_rate / 12 / 100)
        n = Tenure in months
    """
    if principal <= 0 or tenure_months <= 0:
        return {
            "monthly_emi": 0.0,
            "total_interest": 0.0,
            "total_payment": 0.0,
            "principal": principal,
            "tenure_months": tenure_months,
            "annual_rate": annual_rate,
            "principal_pct": 100.0,
            "interest_pct": 0.0,
        }

    monthly_rate = (annual_rate / 100.0) / 12.0

    if monthly_rate == 0:
        monthly_emi = principal / tenure_months
        total_payment = principal
        total_interest = 0.0
    else:
        compounded = math.pow(1 + monthly_rate, tenure_months)
        monthly_emi = (principal * monthly_rate * compounded) / (compounded - 1)
        total_payment = monthly_emi * tenure_months
        total_interest = total_payment - principal

    principal_pct = (principal / total_payment * 100.0) if total_payment > 0 else 100.0
    interest_pct = (total_interest / total_payment * 100.0) if total_payment > 0 else 0.0

    return {
        "monthly_emi": round(monthly_emi, 2),
        "total_interest": round(total_interest, 2),
        "total_payment": round(total_payment, 2),
        "principal": round(principal, 2),
        "tenure_months": tenure_months,
        "annual_rate": round(annual_rate, 2),
        "principal_pct": round(principal_pct, 1),
        "interest_pct": round(interest_pct, 1),
    }


def generate_amortization_schedule(principal: float, annual_rate: float, tenure_months: int):
    """
    Generates monthly and yearly amortization schedules with balance breakdown.
    """
    base_data = calculate_emi_data(principal, annual_rate, tenure_months)
    monthly_emi = base_data["monthly_emi"]
    monthly_rate = (annual_rate / 100.0) / 12.0

    balance = principal
    monthly_schedule = []
    yearly_schedule = {}

    for month in range(1, tenure_months + 1):
        interest_for_month = balance * monthly_rate
        principal_for_month = monthly_emi - interest_for_month

        # Boundary correction for last month
        if balance < principal_for_month or month == tenure_months:
            principal_for_month = balance
            monthly_emi_actual = principal_for_month + interest_for_month
            closing_balance = 0.0
        else:
            monthly_emi_actual = monthly_emi
            closing_balance = balance - principal_for_month

        opening_balance = balance
        balance = max(0.0, closing_balance)
        paid_pct = round(((principal - balance) / principal) * 100.0, 1)

        year_num = (month - 1) // 12 + 1

        month_record = {
            "period": month,
            "year": year_num,
            "opening_balance": round(opening_balance, 2),
            "emi": round(monthly_emi_actual, 2),
            "principal_paid": round(principal_for_month, 2),
            "interest_paid": round(interest_for_month, 2),
            "closing_balance": round(balance, 2),
            "paid_pct": paid_pct,
        }
        monthly_schedule.append(month_record)

        if year_num not in yearly_schedule:
            yearly_schedule[year_num] = {
                "year": year_num,
                "opening_balance": round(opening_balance, 2),
                "total_emi": 0.0,
                "principal_paid": 0.0,
                "interest_paid": 0.0,
                "closing_balance": 0.0,
                "paid_pct": 0.0,
            }

        yearly_schedule[year_num]["total_emi"] += monthly_emi_actual
        yearly_schedule[year_num]["principal_paid"] += principal_for_month
        yearly_schedule[year_num]["interest_paid"] += interest_for_month
        yearly_schedule[year_num]["closing_balance"] = round(balance, 2)
        yearly_schedule[year_num]["paid_pct"] = paid_pct

    yearly_list = []
    for y, item in yearly_schedule.items():
        yearly_list.append({
            "year": y,
            "opening_balance": round(item["opening_balance"], 2),
            "total_emi": round(item["total_emi"], 2),
            "principal_paid": round(item["principal_paid"], 2),
            "interest_paid": round(item["interest_paid"], 2),
            "closing_balance": round(item["closing_balance"], 2),
            "paid_pct": item["paid_pct"],
        })

    return {
        "summary": base_data,
        "yearly": yearly_list,
        "monthly": monthly_schedule,
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/calculate-emi", methods=["POST", "GET"])
def api_calculate_emi():
    if request.method == "POST":
        data = request.get_json(silent=True) or request.form
    else:
        data = request.args

    try:
        principal = float(data.get("principal", 1000000))
        rate = float(data.get("interest_rate", 8.5))
        tenure_value = float(data.get("tenure_value", 20))
        tenure_unit = data.get("tenure_unit", "years").lower()

        tenure_months = int(tenure_value * 12) if tenure_unit == "years" else int(tenure_value)
        result = calculate_emi_data(principal, rate, tenure_months)
        return jsonify({"success": True, "data": result})
    except (ValueError, TypeError) as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/amortization-schedule", methods=["POST", "GET"])
def api_amortization():
    if request.method == "POST":
        data = request.get_json(silent=True) or request.form
    else:
        data = request.args

    try:
        principal = float(data.get("principal", 1000000))
        rate = float(data.get("interest_rate", 8.5))
        tenure_value = float(data.get("tenure_value", 20))
        tenure_unit = data.get("tenure_unit", "years").lower()

        tenure_months = int(tenure_value * 12) if tenure_unit == "years" else int(tenure_value)
        schedule = generate_amortization_schedule(principal, rate, tenure_months)
        return jsonify({"success": True, "data": schedule})
    except (ValueError, TypeError) as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/health")
def api_health():
    return jsonify({"status": "ok", "service": "StreamEMI Financial Analytics", "version": "1.0.0"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
