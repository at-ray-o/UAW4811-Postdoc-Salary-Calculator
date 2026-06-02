#@title Run this cell and check your predicted salary on the target date
# =========================
# SETUP
# =========================

# Install widgets if needed



from google.colab import output
output.enable_custom_widget_manager()

from datetime import date
from dateutil.relativedelta import relativedelta
import ipywidgets as widgets
from IPython.display import display, clear_output


# =========================
# UC SCALE MODEL
# =========================

BASE = {
    0: 64480,
    1: 66868,
    2: 69342,
    3: 71908,
    4: 74569,
    5: 77327
}

def scale(d):
    m = 1.0
    for x in [date(2024,10,1), date(2025,10,1), date(2026,10,1)]:
        if d >= x:
            m *= 1.035
    return {k: v * m for k, v in BASE.items()}


def level(months):
    return min(months // 12, 5)


def months_since(join, prev_exp, d):
    r = relativedelta(d, join)
    return prev_exp + r.years * 12 + r.months


def review_month(join):
    md = (join.month, join.day)
    return 10 if (md <= (4, 1) or md >= (10, 1)) else 4


def step_salary(salary, scale_min):
    """
    Apply 3% raise + enforce scale floor
    ONLY at review points.
    """
    return max(salary * 1.03, scale_min)


# =========================
# SIMULATION ENGINE
# =========================

def simulate(join, prev_exp, start_salary, end_date):
    rm = review_month(join)

    cur = join.replace(day=1)
    end_date = end_date.replace(day=1)

    salary = start_salary
    path = {cur: salary}

    while cur < end_date:
        nxt = cur + relativedelta(months=1)

        if nxt.month == rm:
            lvl = level(months_since(join, prev_exp, nxt))
            min_salary = scale(nxt)[lvl] / 12
            salary = step_salary(salary, min_salary)

        path[nxt] = salary
        cur = nxt

    return path


# =========================
# CORE LOGIC (YOUR 3 RULES)
# =========================

def run_model(join, prev_exp,
              start_salary,
              current_salary,
              salary_date,
              target_date):

    if None in (join, salary_date, target_date):
        raise ValueError("All dates must be filled")

    salary_date = salary_date.replace(day=1)
    target_date = target_date.replace(day=1)

    # -------------------------------------------------
    # 1. STARTING SALARY CHECK
    # -------------------------------------------------
    start_lvl = level(0)
    start_min = scale(join)[start_lvl] / 12

    if start_salary < start_min:
        raise ValueError(
            f"STARTING SALARY BELOW SCALE\n"
            f"Expected ≥ {start_min:.2f}\n"
            f"Got      {start_salary:.2f}"
        )

    # -------------------------------------------------
    # 2. AUDIT: START → CURRENT
    # -------------------------------------------------
    audit_path = simulate(join, prev_exp, start_salary, salary_date)

    expected_current = audit_path.get(salary_date)

    if current_salary < expected_current:
        raise ValueError(
            f"UNDERPAID AT {salary_date.strftime('%Y-%m')}\n\n"
            f"Expected: {expected_current:.2f}\n"
            f"Actual:   {current_salary:.2f}"
        )

    # -------------------------------------------------
    # 3. FORECAST: CONTINUE FROM ACTUAL SALARY (NO RE-SIMULATION)
    # -------------------------------------------------

    rm = review_month(join)

    cur = salary_date.replace(day=1)
    end = target_date.replace(day=1)

    salary = current_salary
    future = {cur: salary}

    while cur < end:
        nxt = cur + relativedelta(months=1)

        if nxt.month == rm:
            lvl = level(months_since(join, prev_exp, nxt))
            min_salary = scale(nxt)[lvl] / 12

            # IMPORTANT: 3% applies to ACTUAL salary only
            salary = max(salary * 1.03, min_salary)

        future[nxt] = salary
        cur = nxt

    return expected_current, future


# =========================
# UI
# =========================

join = widgets.DatePicker(description="Join Date",style={'description_width': 'initial'})
prev = widgets.IntText(description="Prev Exp (months)", value=0,style={'description_width': 'initial'})

start = widgets.FloatText(description="Starting salary on join", value=6000,style={'description_width': 'initial'})
current = widgets.FloatText(description="Salary at given date", value=6500,style={'description_width': 'initial'})

salary_date = widgets.DatePicker(description="Salary Date",style={'description_width': 'initial'})
target_date = widgets.DatePicker(description="Target Date",style={'description_width': 'initial'})

btn = widgets.Button(description="Run", button_style="success")
out = widgets.Output()


def on_click(_):
    with out:
        clear_output()
        try:
            expected, future = run_model(
                join.value,
                prev.value,
                start.value,
                current.value,
                salary_date.value,
                target_date.value
            )

            print("=== SALARY MODEL ===\n")
            print("Expected at salary date:", round(expected, 2))
            print("\nFuture projection:\n")

            for i, (d, s) in enumerate(future.items()):
                if i > 12:
                    break
                print(d.strftime("%Y-%m"), "→", round(s, 2))

        except Exception as e:
            print("ERROR:", e)


btn.on_click(on_click)

display(widgets.VBox([
    join, prev, start, current,
    salary_date, target_date,
    btn, out
]))
