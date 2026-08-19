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
    statement = load_and_categorize_statement(file_path)

    expenses = statement[
        statement["type"].str.upper() == "DEBIT"
    ].copy()

    expenses["description_upper"] = expenses["description"].str.upper()

    results = []

    for keyword in KNOWN_SUBSCRIPTIONS:
        matches = expenses[
            expenses["description_upper"].str.contains(keyword, na=False)
        ]

        if not matches.empty:
            results.append(
                {
                    "subscription": keyword,
                    "times_charged": len(matches),
                    "total_spent": matches["amount"].sum(),
                    "average_charge": round(matches["amount"].mean(), 2),
                    "potential_subscription": True,
                }
            )

    return pd.DataFrame(results)


if __name__ == "__main__":
    result = detect_subscriptions(
        "data/sample_statement.csv"
    )

    print(result)