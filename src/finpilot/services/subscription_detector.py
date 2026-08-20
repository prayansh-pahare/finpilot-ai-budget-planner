import pandas as pd

from statement_parser import load_and_categorize_statement


KNOWN_SUBSCRIPTIONS = [
    "NETFLIX",
    "SPOTIFY",
    "PRIME VIDEO",
    "YOUTUBE",
    "GYM",
    "ADOBE",
    "MICROSOFT",
]


def detect_subscriptions(file_path: str) -> pd.DataFrame:
    """Detect likely recurring subscriptions."""

    statement = load_and_categorize_statement(file_path)

    expenses = statement[
        statement["type"].str.upper() == "DEBIT"
    ].copy()

    expenses["date"] = pd.to_datetime(expenses["date"])

    expenses["description_upper"] = (
        expenses["description"]
        .astype(str)
        .str.upper()
    )

    results = []

    for keyword in KNOWN_SUBSCRIPTIONS:

        matches = expenses[
            expenses["description_upper"]
            .str.contains(keyword, na=False)
        ].copy()

        if matches.empty:
            continue

        times_charged = len(matches)

        unique_months = matches["date"].dt.to_period("M").nunique()

        average_charge = matches["amount"].mean()

        if average_charge > 0:
            amount_variation = (
                matches["amount"].std(ddof=0)
                / average_charge
            )
        else:
            amount_variation = 0

        recurring = (
            times_charged >= 2
            and unique_months >= 2
            and amount_variation <= 0.10
        )

        results.append(
            {
                "subscription": keyword,
                "times_charged": times_charged,
                "months_detected": unique_months,
                "average_charge": round(
                    float(average_charge), 2
                ),
                "total_spent": round(
                    float(matches["amount"].sum()), 2
                ),
                "recurring": recurring,
            }
        )

    return pd.DataFrame(results)


if __name__ == "__main__":

    result = detect_subscriptions(
        "data/sample_statement.csv"
    )

    print(result)