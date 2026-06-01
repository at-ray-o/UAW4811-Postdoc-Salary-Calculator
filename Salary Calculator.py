"""
UC Postdoctoral Scholar Monthly Salary Calculator
=================================================

Estimate a UC postdoc's EXPECTED MONTHLY SALARY next month under the
UC–UAW 5810 contract.

Inputs
------
join_date : datetime.date
    Initial UC appointment date.

previous_experience_months : int
    Postdoctoral experience accumulated before joining UC.

current_monthly_salary : float
    Current monthly salary.

How raises are determined
-------------------------
The contract specifies annual review dates:

    Hire date Oct 1 – Apr 1  -> Oct 1 review
    Hire date Apr 2 – Sep 30 -> Apr 1 review

If next month contains the review date, salary becomes the greater of:

    1. Current salary × 1.03
    2. Experience-level minimum salary

The contractual salary scale is annual, so this script converts it to
monthly salary before comparison.

Returns
-------
A dictionary containing:
    - next month
    - whether a raise applies
    - experience level
    - current monthly salary
    - expected monthly salary next month
"""

from datetime import date
from dateutil.relativedelta import relativedelta


# Contract salary scale effective Oct 1, 2023 (ANNUAL salaries)
BASE_SCALE = {
    0: 64480,
    1: 66868,
    2: 69342,
    3: 71908,
    4: 74569,
    5: 77327,
}


def get_salary_scale(on_date):
    """
    Return annual salary scale in effect on a given date.
    """

    multiplier = 1.0

    for raise_date in (
        date(2024, 10, 1),
        date(2025, 10, 1),
        date(2026, 10, 1),
    ):
        if on_date >= raise_date:
            multiplier *= 1.035

    return {
        level: annual_salary * multiplier
        for level, annual_salary in BASE_SCALE.items()
    }


def get_experience_months(
    join_date,
    previous_experience_months,
    on_date,
):
    """
    Total postdoctoral experience in months.
    """

    rd = relativedelta(on_date, join_date)

    months_at_uc = rd.years * 12 + rd.months

    return previous_experience_months + months_at_uc


def get_experience_level(experience_months):
    """
    UC experience level.

    Level 0 : 0-11 months
    Level 1 : 12-23 months
    Level 2 : 24-35 months
    Level 3 : 36-47 months
    Level 4 : 48-59 months
    Level 5 : 60-71 months
    """

    return min(experience_months // 12, 5)


def get_review_month(join_date):
    """
    Determine annual review month according to contract.
    """

    md = (join_date.month, join_date.day)

    if md >= (10, 1) or md <= (4, 1):
        return 10  # October review

    return 4  # April review


def expected_salary_next_month(
    join_date,
    previous_experience_months,
    current_monthly_salary,
    current_date=None,
):
    """
    Calculate expected MONTHLY salary next month.
    """

    if current_date is None:
        current_date = date.today()

    # First day of next month
    next_month = (
        current_date.replace(day=1)
        + relativedelta(months=1)
    )

    review_month = get_review_month(join_date)

    raise_applies = next_month.month == review_month

    experience_months = get_experience_months(
        join_date,
        previous_experience_months,
        next_month,
    )

    level = get_experience_level(experience_months)

    expected_monthly_salary = current_monthly_salary

    if raise_applies:

        annual_scale = get_salary_scale(next_month)

        # Convert annual minimum to monthly minimum
        experience_minimum_monthly = (
            annual_scale[level] / 12.0
        )

        three_percent_raise_monthly = (
            current_monthly_salary * 1.03
        )

        expected_monthly_salary = max(
            experience_minimum_monthly,
            three_percent_raise_monthly,
        )

    return {
        "next_month": next_month.isoformat(),
        "raise_applies": raise_applies,
        "experience_months": experience_months,
        "experience_level": level,
        "current_monthly_salary": round(
            current_monthly_salary, 2
        ),
        "expected_monthly_salary_next_month": round(
            expected_monthly_salary, 2
        ),
    }


# ------------------------------------------------------------------
# Example
# ------------------------------------------------------------------

if __name__ == "__main__":

    result = expected_salary_next_month(
        join_date=date(2024, 7, 15),
        previous_experience_months=18,
        current_monthly_salary=6250.00,
    )

    print("\nUC Postdoc Salary Estimate\n")

    for key, value in result.items():
        print(f"{key:35s}: {value}")
