import re

def verify_ratios(ratios, text):
    issues = []

    # Sanity ranges
    ranges = {
        "pe":               (0, 200),
        "debt_equity":      (0, 10),
        "roe":              (-50, 100),
        "roa":              (-50, 100),
        "current_ratio":    (0, 20),
        "operating_margin": (-100, 100),
        "net_margin":       (-100, 100),
        "eps":              (-1000, 10000),
        "book_value":       (0, 100000),
        "dividend_yield":   (0, 50),
    }

    for key, (low, high) in ranges.items():
        val = ratios.get(key)
        if val is not None and not (low <= val <= high):
            issues.append(f"{key} range se bahar: {val} (expected {low} to {high})")

    for key, val in ratios.items():
        if val is None:
            issues.append(f"{key}: PDF mein nahi mila")

    return {"verified": len(issues) == 0, "issues": issues}
def verify_summary(summary, ratios):
    problems = []
    numbers = re.findall(r"\d+\.?\d*", summary)

    for n in numbers:
        n_f = float(n)
        if not any(
            ratios[k] is not None and abs(ratios[k] - n_f) < 0.05
            for k in ratios
        ):
            problems.append(f"Summary mein extra number: {n}")

    return {"clean": len(problems) == 0, "problems": problems}